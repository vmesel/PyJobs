from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from raven.contrib.django.raven_compat.models import client

from pyjobs.core.email_utils import (
    contact_email,
    contato_cadastrado_empresa,
    contato_cadastrado_pessoa,
    vaga_publicada,
)
from pyjobs.core.managers import PublicQuerySet
from pyjobs.core.newsletter import subscribe_user_to_chimp
from pyjobs.core.utils import post_telegram_channel


class Messages(models.Model):
    message_title = models.CharField(
        "Título da Mensagem", max_length=100, default="", blank=False
    )

    message_type = models.CharField(
        "Ticker usado no backend para ID da msg",
        default="offer",
        max_length=200,
        blank=False,
    )

    message_content = models.TextField("Texto do E-mail", default="")

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.URLField(verbose_name="GitHub", blank=True, default="")
    linkedin = models.URLField(verbose_name="LinkedIn", blank=True, default="")
    portfolio = models.URLField(verbose_name="Portfolio", blank=True, default="")
    cellphone = models.CharField(
        verbose_name="Telefone",
        max_length=16,
        validators=[
            RegexValidator(
                regex="^((?:\([1-9]{2}\)|\([1-9]{2}\) |[1-9]{2}|[1-9]{2} )(?:[2-8]|9[1-9])[0-9]{3}(?:\-[0-9]{4}| [0-9]{4}|[0-9]{4}))$",
                message="Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen.",
            )
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skill")

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __repr__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ["-created_at"]

    def profile_skill_grade(self, job):
        skills = self.skills.values_list("pk", flat=True)
        if not skills:
            return False

        required = Job.objects.get(pk=job).skills.values_list("pk", flat=True)
        if not required:
            return 0

        intersect = set(skills) & set(required)
        return (len(intersect) / len(required)) * 100


class Job(models.Model):
    title = models.CharField(
        "Título da Vaga",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: Desenvolvedor",
    )
    workplace = models.CharField(
        "Local",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: Santana - São Paulo",
    )
    company_name = models.CharField(
        "Nome da Empresa",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: ACME Inc",
    )
    application_link = models.URLField(
        verbose_name="Link para a Vaga",
        blank=True,
        default="",
        help_text="Ex.: http://goo.gl/hahaha",
    )
    company_email = models.EmailField(
        verbose_name="Email da Empresa", blank=False, help_text="Ex.: abc@def.com"
    )
    description = models.TextField(
        "Descrição da vaga",
        default="",
        help_text="Descreva um pouco da sua empresa e da vaga, tente ser breve",
    )
    requirements = models.TextField(
        "Requisitos da vaga",
        default="",
        help_text="Descreva os requisitos da sua empresa em bullet points\n\n-Usar Git\n-Saber Java",
    )
    premium = models.BooleanField("Premium?", default=False)
    public = models.BooleanField("Público?", default=True)
    ad_interested = models.BooleanField("Impulsionar*", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skill")

    objects = models.Manager.from_queryset(PublicQuerySet)()

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return self.title

    def get_application_link(self):
        return self.application_link if self.application_link != "" else False

    def get_premium_jobs():
        return Job.objects.premium().created_in_the_last(30)[:7]

    def get_publicly_available_jobs(term=None):
        return Job.objects.not_premium().created_in_the_last(30).search(term)

    def get_feed_jobs():
        return Job.objects.not_premium().created_in_the_last(7)

    def get_excerpt(self):
        return self.description[:500]

    def applied(self, request_user):
        return JobApplication.objects.filter(job=self, user=request_user).exists()

    def apply(self, request_user):
        JobApplication.objects.create(job=self, user=request_user)
        return True

    def get_weekly_summary(self):
        return Job.objects.created_in_the_last(7)

    def get_absolute_url(self):
        return "/job/{}".format(self.pk)


class JobApplication(models.Model):
    user = models.ForeignKey(User, default="")
    job = models.ForeignKey(Job, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

    def __str__(self):
        return "{} applied to {}".format(self.user, self.job)


class Contact(models.Model):
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    subject = models.CharField("Assunto", max_length=100, default="", blank=False)
    email = models.EmailField("Email", default="", blank=False)
    message = models.TextField("Mensagem", default="", blank=False)


class Skill(models.Model):
    name = models.CharField("Skill", max_length=100, default="", blank=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@receiver(post_save, sender=Profile)
def add_user_to_mailchimp(sender, instance, created, **kwargs):
    subscribe_user_to_chimp(instance)


@receiver(post_save, sender=JobApplication)
def send_email_notifing_job_application(sender, instance, created, **kwargs):
    msg_email_person = contato_cadastrado_pessoa(
        pessoa=instance.user, vaga=instance.job
    )
    msg_email_company = contato_cadastrado_empresa(
        pessoa=instance.user, vaga=instance.job
    )

    send_mail(
        "Parabéns! Você se inscreveu na vaga!",
        msg_email_person,
        "pyjobs@pyjobs.com.br",
        [instance.user.email],
    )
    send_mail(
        "Você possui mais um candidato para a sua vaga",
        msg_email_company,
        "pyjobs@pyjobs.com.br",
        [instance.job.company_email],
    )


def send_offer_email_template(job):
    message = Messages.objects.filter(message_type="offer")[0]
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        "vinicius@pyjobs.com.br",
        [job.company_email, "viniciuscarqueijo@gmail.com"],
    )


def send_feedback_collection_email(job):
    message = Messages.objects.filter(message_type="feedback")[0]
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        "vinicius@pyjobs.com.br",
        [job.company_email, "viniciuscarqueijo@gmail.com"],
    )


@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    if created:
        job = instance.title
        empresa = instance.company_name
        local = instance.workplace
        link = instance.pk
        message_text = "Nova oportunidade! {} - {} em {}\n http://www.pyjobs.com.br/job/{}/".format(
            job, empresa, local, link
        )
        post_telegram_channel(message_text)
        msg_email = vaga_publicada(
            empresa=instance.company_name, vaga=instance.title, pk=instance.pk
        )

        send_mail(
            "Sua oportunidade está disponível no PyJobs",
            msg_email,
            "pyjobs@pyjobs.com.br",
            [instance.company_email],
        )
        try:
            send_offer_email_template(instance)
        except:
            client.captureException()


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    msg_email = contact_email(
        instance.name, instance.email, instance.subject, instance.message
    )
    send_mail(
        "Contato PyJobs: {}".format(instance.subject),
        msg_email,
        "pyjobs@pyjobs.com.br",
        ["viniciuscarqueijo@gmail.com"],
    )
