from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from pyjobs.core.email_utils import get_email_with_template
from pyjobs.core.models import Job


class MailingList(models.Model):
    email = models.EmailField("Email", default="", blank=False)
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    slug = models.CharField("Slug", max_length=100, default="", blank=False)

    class Meta:
        verbose_name = "Lista de e-mail"
        verbose_name_plural = "Listas de e-mail"


class Contact(models.Model):
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    subject = models.CharField("Assunto", max_length=100, default="", blank=False)
    email = models.EmailField("Email", default="", blank=False)
    message = models.TextField("Mensagem", default="", blank=False)

    class Meta:
        verbose_name = "Resposta de Contato"
        verbose_name_plural = "Respostas de contatos"


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


class Share(models.Model):
    user_sharing = models.ForeignKey(User)

    user_receiving_email = models.EmailField(
        "E-mail para enviarmos a indicação", null=False, blank=False
    )

    job = models.ForeignKey(Job)

    class Meta:
        verbose_name = "Indicação"
        verbose_name_plural = "Indicações"


class CustomerQuote(models.Model):
    customer_name = models.CharField("Nome do cliente", max_length=500)

    company_name = models.CharField("Nome da empresa", max_length=500)

    avatar_name = models.CharField("Nome da imagem estatica do avatar", max_length=500)

    customer_quote = models.TextField("Texto do depoimento")


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    email_context = {"mensagem": instance}
    msg = get_email_with_template(
        "new_contact", email_context, instance.subject, [settings.WEBSITE_OWNER_EMAIL]
    )
    msg.send()


@receiver(post_save, sender=Share)
def share_to_new_buddy(sender, instance, created, **kwargs):
    email_context = {"pessoa": instance.user_sharing, "vaga": instance.job}
    msg = get_email_with_template(
        "job_sharing",
        email_context,
        "Indicacao de vaga",
        [instance.user_receiving_email],
    )
    msg.send()
