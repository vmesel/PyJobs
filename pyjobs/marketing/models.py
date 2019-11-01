from django.db import models

class MailingList(models.Model):
    email = models.EmailField("Email", default="", blank=False)
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    slug = models.CharField("Slug", max_length=100, default="", blank=False)


class Contact(models.Model):
    name = models.CharField("Nome", max_length=100, default="", blank=False)
    subject = models.CharField("Assunto", max_length=100, default="", blank=False)
    email = models.EmailField("Email", default="", blank=False)
    message = models.TextField("Mensagem", default="", blank=False)
