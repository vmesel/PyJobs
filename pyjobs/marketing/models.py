from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from pyjobs.core.email_utils import get_email_with_template
from pyjobs.core.models import Job
from django.utils.translation import gettext_lazy as _


class MailingList(models.Model):
    email = models.EmailField(_("Email"), default="", blank=False)
    name = models.CharField(_("Nome"), max_length=100, default="", blank=False)
    slug = models.CharField(_("Slug"), max_length=100, default="", blank=False)

    class Meta:
        verbose_name = _("Lista de e-mail")
        verbose_name_plural = _("Listas de e-mail")


class Contact(models.Model):
    name = models.CharField(_("Nome"), max_length=100, default="", blank=False)
    subject = models.CharField(_("Assunto"), max_length=100, default="", blank=False)
    email = models.EmailField(_("Email"), default="", blank=False)
    message = models.TextField(_("Mensagem"), default="", blank=False)

    class Meta:
        verbose_name = _("Resposta de Contato")
        verbose_name_plural = _("Respostas de contatos")


class Messages(models.Model):
    message_title = models.CharField(
        _("Título da Mensagem"), max_length=100, default="", blank=False
    )

    message_type = models.CharField(
        _("Ticker usado no backend para ID da msg"),
        default="offer",
        max_length=200,
        blank=False,
    )

    message_content = models.TextField(_("Texto do E-mail"), default="")

    class Meta:
        verbose_name = _("Mensagem")
        verbose_name_plural = _("Mensagens")


class Share(models.Model):
    user_sharing = models.ForeignKey(User, on_delete=models.PROTECT)

    user_receiving_email = models.EmailField(
        _("E-mail para enviarmos a indicação"), null=False, blank=False
    )

    job = models.ForeignKey(Job, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Indicação")
        verbose_name_plural = _("Indicações")


class CustomerQuote(models.Model):
    customer_name = models.CharField(_("Nome do cliente"), max_length=500)

    company_name = models.CharField(_("Nome da empresa"), max_length=500)

    avatar_name = models.CharField(
        _("Nome da imagem estatica do avatar"), max_length=500
    )

    customer_quote = models.TextField(_("Texto do depoimento"))


class PushMessage(models.Model):
    head = models.CharField(_("Titulo"), max_length=2000)
    body = models.TextField(_("Texto da mensagem"), max_length=2000)
    url = models.URLField(_("Link para a vaga"))


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
        _("Indicacao de vaga"),
        [instance.user_receiving_email],
    )
    msg.send()
