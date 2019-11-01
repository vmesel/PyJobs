from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from pyjobs.core.email_utils import get_email_with_template

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


@receiver(post_save, sender=Contact)
def new_contact(sender, instance, created, **kwargs):
    email_context = {"mensagem": instance}
    msg = get_email_with_template(
        "new_contact", email_context, instance.subject, [settings.WEBSITE_OWNER_EMAIL]
    )
    msg.send()
