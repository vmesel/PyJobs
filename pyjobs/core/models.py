from datetime import datetime, timedelta

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.mail import send_mail

from pyjobs.core.email_utils import *
from pyjobs.core.utils import *
from pyjobs.core.newsletter import *

class Messages(models.Model):
    message_title = models.CharField(
        "Título da Mensagem",
        max_length=100,
        default="",
        blank=False
    )

    message_type = models.CharField(
        "Ticker usado no backend para ID da msg",
        default="offer",
        max_length=200,
        blank=False
    )

    message_content = models.TextField(
        "Texto do E-mail",
        default=""
    )

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.URLField(verbose_name="GitHub", blank=True, default="")
    linkedin = models.URLField(verbose_name="LinkedIn", blank=True, default="")
    portfolio = models.URLField(verbose_name="Portfolio", blank=True, default="")
    cellphone = models.CharField(verbose_name="Telefone",
        max_length=16,
        validators=[
            RegexValidator(
                regex='^((?:\([1-9]{2}\)|\([1-9]{2}\) |[1-9]{2}|[1-9]{2} )(?:[2-8]|9[1-9])[0-9]{3}(?:\-[0-9]{4}| [0-9]{4}|[0-9]{4}))$',
                message="Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen."
            )
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skills")

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __repr__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ['-created_at']

    def profile_skill_grade(self, job_pk):
        job_to_evaluate = Job.objects.get(pk=job_pk)

        job_required_skills = [skill.pk for skill in job_to_evaluate.skills.all()]
        user_skills = [skill.pk for skill in self.skills.all()]

        if len(user_skills) < 1:
            return False

        intersect_skills = [
            skill for skill in user_skills if skill in job_required_skills
        ]
        return (len(intersect_skills)/len(job_required_skills))*100


class Job(models.Model):
    title = models.CharField(
        "Título da Vaga", max_length=100, default="",
        blank=False, help_text = "Ex.: Desenvolvedor"
    )
    workplace = models.CharField(
        "Local", max_length=100, default="",
        blank=False, help_text = "Ex.: Santana - São Paulo"
    )
    company_name = models.CharField(
        "Nome da Empresa", max_length=100, default="",
        blank=False, help_text = "Ex.: ACME Inc"
    )
    application_link = models.URLField(verbose_name="Link para a Vaga", blank=True, default="", help_text = "Ex.: http://goo.gl/hahaha")
    company_email = models.EmailField(verbose_name="Email da Empresa", blank=False, help_text = "Ex.: abc@def.com")
    description = models.TextField("Descrição da vaga", default="", help_text = "Descreva um pouco da sua empresa e da vaga, tente ser breve")
    requirements = models.TextField("Requisitos da vaga", default="", help_text = "Descreva os requisitos da sua empresa em bullet points\n\n-Usar Git\n-Saber Java")
    premium = models.BooleanField("Premium?", default=False)
    public = models.BooleanField("Público?", default=True)
    ad_interested = models.BooleanField("Impulsionar*", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skills")

    def __str__(self):
        return self.title

    def get_application_link(self):
        return self.application_link if self.application_link != "" else False

    def get_premium_jobs():
        return Job.objects.filter(premium=True, public=True,
            created_at__lte=datetime.today(),
            created_at__gt=datetime.today()-timedelta(days=30)
        ).order_by('-created_at')[:5]

    def get_publicly_available_jobs(search_value=None):
        ft = models.Q()

        if search_value is not None:
            ft = models.Q(title__icontains=search_value) | \
                models.Q(workplace__icontains=search_value) | \
                models.Q(description__icontains=search_value) | \
                models.Q(requirements__icontains=search_value)

        return Job.objects.filter(ft, premium=False, public=True,
            created_at__lte=datetime.today(),
            created_at__gt=datetime.today()-timedelta(days=30)
        ).order_by('-created_at')


    def get_feed_jobs():
        return Job.objects.filter(premium=False, public=True,
            created_at__lte=datetime.today(),
            created_at__gt=datetime.today()-timedelta(days=7)
        ).order_by('-created_at')

    def get_excerpt(self):
        return self.description[:500]

    def applied(self, request_user):
        return True if JobApplication.objects.\
            filter(job=self, user=request_user).exists() \
            else False

    def apply(self, request_user):
        JobApplication.objects.create(job=self, user=request_user)
        return True

    def get_weekly_summary(self):
        today = datetime.today()
        past_date = today - timedelta(days=7)
        return Job.objects.filter(
            created_at__gte=past_date,
            created_at__lte=today,
        )

    def get_absolute_url(self):
        return "/job/{}".format(self.pk)


class JobApplication(models.Model):
    user = models.ForeignKey(User, default="")
    job = models.ForeignKey(Job, default="")

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

class Skills(models.Model):
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
    msg_email_person = contato_cadastrado_pessoa(pessoa=instance.user, vaga=instance.job)
    msg_email_company = contato_cadastrado_empresa(pessoa=instance.user, vaga=instance.job)

    send_mail(
        "Parabéns! Você se inscreveu na vaga!",
        msg_email_person,
        "pyjobs@pyjobs.com.br",
        [instance.user.email]
    )
    send_mail(
        "Você possui mais um candidato para a sua vaga",
        msg_email_company,
        "pyjobs@pyjobs.com.br",
        [instance.job.company_email]
    )


def send_offer_email_template(job):
    message = Messages.objects.filter(message_type="offer")[0]
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        "viniciuscarqueijo@gmail.com",
        [job.company_email]
    )

@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    if created == True:
        job=instance.title,
        empresa=instance.company_name,
        local=instance.workplace,
        link=instance.pk
        message_text = f"Nova oportunidade! {job} - {empresa} em {local}\n http://www.pyjobs.com.br/job/{link}/"
        post_fb_page(message_text)
        post_telegram_channel(message_text)
        msg_email = vaga_publicada(empresa=instance.company_name, vaga=instance.title, pk=instance.pk)
        send_mail(
            "Sua oportunidade está disponível no PyJobs",
            msg_email,
            "pyjobs@pyjobs.com.br",
            [instance.company_email]
        )
        if instance.ad_interested:
            try:
                send_offer_email_template(instance)
            except:
                pass


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    msg_email = contact_email(instance.name, instance.email, instance.subject, instance.message)
    send_mail(
        "Contato PyJobs: {}".format(instance.subject),
        msg_email,
        "pyjobs@pyjobs.com.br",
        ["viniciuscarqueijo@gmail.com"]
    )
