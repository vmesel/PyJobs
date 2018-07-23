from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from decouple import config
from django.core.mail import send_mail
from core.email_utils import *
from core.utils import *

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
                message="Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen.")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ['-created_at']


class Job(models.Model):
    title = models.CharField("Título da Vaga", max_length=100, default="", blank=False)
    workplace = models.CharField("Local", max_length=100, default="", blank=False)
    company_name = models.CharField("Nome da Empresa", max_length=100, default="", blank=False)
    application_link = models.URLField(verbose_name="Link para a Vaga", blank=True, default="")
    company_email = models.EmailField(verbose_name="Email da Empresa", blank=False)
    description = models.TextField("Descrição da vaga", default="")
    requirements = models.TextField("Requisitos da vaga", default="")
    premium = models.BooleanField("Premium?", default=False)
    public = models.BooleanField("Público?", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_application_link(self):
        if self.application_link != "":
            return self.application_link
        else:
            return False

    def get_premium_jobs():
        return Job.objects.filter(premium=True, public=True).order_by('-created_at')[:2]

    def get_publicly_available_jobs():
        return Job.objects.filter(premium=False, public=True).order_by('-created_at')

    def get_excerpt(self):
        return self.description[:500]

    def applied(self, request_user):
        if JobApplication.objects.filter(job=self, user=request_user).exists():
            return True
        else:
            return False

    def apply(self, request_user):
        JobApplication.objects.create(job=self, user=request_user)
        return True


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


@receiver(post_save, sender=JobApplication)
def send_email_notifing_job_application(sender, instance, created, **kwargs):
    msg_email_person = contato_cadastrado_pessoa(pessoa=instance.user, vaga=instance.job)
    msg_email_company = contato_cadastrado_empresa(pessoa=instance.user, vaga=instance.job)
    receiver_person = [instance.user.email]
    receiver_company = [instance.job.company_email]
    send_mail(
        "Parabéns! Você se inscreveu na vaga!",
        msg_email_person,
        "pyjobs@pyjobs.com.br",
        receiver_person
    )
    send_mail(
        "Você possui mais um candidato para a sua vaga",
        msg_email_company,
        "pyjobs@pyjobs.com.br",
        receiver_company
    )


@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    message_text = "Nova oportunidade! {job} - {empresa} em {local}\n http://www.pyjobs.com.br/job/{link}/".format(
        job=instance.title,
        empresa=instance.company_name,
        local=instance.workplace,
        link=instance.pk
    )
    post_fb_page(message_text)
    post_telegram_channel(message_text)
    msg_email = vaga_publicada(empresa=instance.company_name, vaga=instance.title, pk=instance.pk)
    receivers = [instance.company_email]
    send_mail(
        "Sua oportunidade está disponível no PyJobs",
        msg_email,
        "pyjobs@pyjobs.com.br",
        receivers
    )


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    msg_email = contact_email(instance.name, instance.email, instance.subject, instance.message)
    send_mail(
        "Contato PyJobs: {}".format(instance.subject),
        msg_email,
        "pyjobs@pyjobs.com.br",
        ["viniciuscarqueijo@gmail.com"]
    )
