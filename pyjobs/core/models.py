from datetime import timedelta
from hashlib import sha512

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from raven.contrib.django.raven_compat.models import client


from pyjobs.settings import SECRET_KEY
from pyjobs.core.managers import PublicQuerySet, ProfilingQuerySet
from pyjobs.core.newsletter import subscribe_user_to_mailer
from pyjobs.core.utils import post_telegram_channel
from pyjobs.core.email_utils import get_email_with_template


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


STATE_CHOICES = [
    (0, "Acre"),
    (1, "Alagoas"),
    (2, "Amapá"),
    (3, "Amazonas"),
    (4, "Bahia"),
    (5, "Ceará"),
    (6, "Distrito Federal"),
    (7, "Espírito Santo"),
    (8, "Goiás"),
    (9, "Maranhão"),
    (10, "Mato Grosso"),
    (11, "Mato Grosso do Sul"),
    (12, "Minas Gerais"),
    (13, "Pará"),
    (14, "Paraíba"),
    (15, "Paraná"),
    (16, "Pernambuco"),
    (17, "Piauí"),
    (18, "Rio de Janeiro"),
    (19, "Rio Grande do Norte"),
    (20, "Rio Grande do Sul"),
    (21, "Rondônia"),
    (22, "Roraima"),
    (23, "Santa Catarina"),
    (24, "São Paulo"),
    (25, "Sergipe"),
    (26, "Tocantins"),
    (27, "Indeterminado"),
]

SALARY_RANGES = [
    (1, "R$ 0,00 a R$ 1.000,00"),
    (2, "R$ 1.000,01 a R$ 3.000,00"),
    (3, "R$ 3.000,01 a R$ 6.000,00"),
    (4, "R$ 6.000,01 a R$ 10.000,00"),
    (5, "R$ 10.000,01 ou mais"),
    (6, "A combinar"),
]

JOB_LEVELS = [
    (1, "Estágio"),
    (2, "Junior"),
    (3, "Pleno"),
    (4, "Sênior"),
    (5, "Indeterminado"),
]


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
    state = models.IntegerField("Seu Estado", choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        "Sua Faixa Salarial Atual", choices=SALARY_RANGES, default=6
    )
    job_level = models.IntegerField("Seu nível atual", choices=JOB_LEVELS, default=5)
    bio = models.TextField(
        "Sua Bio",
        default="",
        help_text="Descreva um pouco sobre você para as empresas poderem te conhecer melhor!",
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

    objects = models.Manager.from_queryset(ProfilingQuerySet)()

    def profile_skill_grade(self, job):
        skills = self.skills.values_list("pk", flat=True)
        job_skills = Job.objects.get(pk=job).skills.values_list("pk", flat=True)
        return Profile.objects.grade(skills, job_skills)


class JobError(Exception):
    pass


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
    premium_at = models.DateTimeField(
        "Data de mudança de Status", blank=True, null=True
    )
    cellphone = models.CharField(
        verbose_name="WhatsApp para contato",
        max_length=16,
        help_text="Deixe seu WhatsApp para contatarmos sobre nossos serviços",
        null=True,
    )
    skills = models.ManyToManyField("Skill")
    is_open = models.BooleanField("Vaga aberta", default=True)
    is_challenging = models.BooleanField("Enviar Chall", default=False)
    challenge = models.TextField("Challenge", blank=True, null=True)

    # Filtering parts of the model

    ## This will allow users to filter on the homepage for jobs that respect their
    ## values, necessities or expectations

    state = models.IntegerField("Estado", choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        "Faixa Salarial", choices=SALARY_RANGES, default=6
    )
    job_level = models.IntegerField(
        "Nível do Profissional", choices=JOB_LEVELS, default=5
    )
    remote = models.BooleanField("Esta vaga é remota?", default=False)

    objects = models.Manager.from_queryset(PublicQuerySet)()

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return self.title

    def get_application_link(self):
        return self.application_link if self.application_link != "" else False

    def get_premium_jobs():
        return Job.objects.premium().created_in_the_last(30, premium=True)[:7]

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

    def get_jobs_to_get_feedback(self):
        return Job.objects.created_days_ago(14)

    def get_expiration_date(self):
        return self.created_at + timedelta(days=30)

    def close_hash(self, salt=None):
        if not all((self.pk, self.created_at)):
            raise JobError("Unsaved Job models have no close hash")

        salt = salt or SECRET_KEY
        value = "::".join(("close", salt, str(self.pk), str(self.created_at)))
        obj = sha512(value.encode("utf-8"))
        return obj.hexdigest()

    def get_close_url(self):
        if not all((self.pk, self.created_at)):
            raise JobError("Unsaved Job models have no close URL")

        kwargs = {"pk": self.pk, "close_hash": self.close_hash()}
        return reverse("close_job", kwargs=kwargs)


class JobApplication(models.Model):
    user = models.ForeignKey(User, default="", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, default="", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    challenge_response_link = models.URLField(default="", blank=True, null=True)
    challenge_response_at = models.DateTimeField(blank=True, null=True)

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


class MailingList(models.Model):
    email = models.EmailField("Email", default="", blank=False)
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    slug = models.CharField("Slug", max_length=100, default="", blank=False)


@receiver(post_save, sender=Profile)
def add_user_to_mailchimp(sender, instance, created, **kwargs):
    subscribe_user_to_mailer(instance)


@receiver(post_save, sender=JobApplication)
def send_email_notifing_job_application(sender, instance, created, **kwargs):
    person_email_context = {"vaga": instance.job, "pessoa": instance.user.profile}

    company_email_context = person_email_context

    msg_email_person = get_email_with_template(
        "job_application_registered",
        person_email_context,
        "Parabéns! Você se inscreveu na vaga!",
        [instance.user.email],
    )
    msg_email_person.send()

    msg_email_company = get_email_with_template(
        "job_applicant",
        company_email_context,
        "Você possui mais um candidato para a sua vaga",
        [instance.job.company_email],
    )
    msg_email_company.send()


def send_offer_email_template(job):
    message = Messages.objects.filter(message_type="offer").first()
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        settings.WEBSITE_OWNER_EMAIL,
        [job.company_email, "viniciuscarqueijo@gmail.com"],
    )


def send_feedback_collection_email(job):
    message = Messages.objects.filter(message_type="feedback")[0]
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        settings.WEBSITE_OWNER_EMAIL,
        [job.company_email, settings.WEBSITE_OWNER_EMAIL],
    )


@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    if not created:
        return

    # post to telegram
    message_base = "Nova oportunidade! {} - {} em {}\n {}/job/{}/"
    message_text = message_base.format(
        instance.title,
        instance.company_name,
        instance.workplace,
        settings.WEBSITE_HOME_URL,
        instance.pk,
    )
    post_telegram_channel(message_text)

    msg = get_email_with_template(
        "published_job",
        {"vaga": instance},
        "Sua oportunidade está disponível no {}".format(settings.WEBSITE_NAME),
        [instance.company_email],
    )
    msg.send()
    try:
        send_offer_email_template(instance)
    except:
        client.captureException()


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    email_context = {"mensagem": instance}
    msg = get_email_with_template(
        "new_contact", email_context, instance.subject, [settings.WEBSITE_OWNER_EMAIL]
    )
    msg.send()
