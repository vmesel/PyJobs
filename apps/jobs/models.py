from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User

from apps.core.models import Company
from apps.emailtools.utils import empresa_cadastrou_vaga, contato_cadastrado, user_cadastrado


class Job(models.Model):
    titulo_do_job = models.CharField("Título do job", max_length=100, default="")
    empresa = models.ForeignKey(Company)
    home_office = models.BooleanField("Aceita home office", default=False)
    descricao = models.TextField("Descrição do job", default="")
    requisitos = models.TextField("Requisitos para o Job", default="")
    data_adicionado = models.DateTimeField("Data que o job foi adicionado", auto_now_add=True)
    local = models.CharField("Local da vaga", max_length=100, default="", help_text="Preencha com o lugar da vaga, caso seja remota, explicite!")
    tipo_freela = models.BooleanField("O job é freela?", default=1, help_text="Selecione apenas se o job for para freelancers")
    publico = models.BooleanField("Este job é público?", default=0)

    class Meta:
        verbose_name = 'Vaga'
        verbose_name_plural = 'Vagas'
        ordering = ['-data_adicionado']

    def __str__(self):
        return self.titulo_do_job


class InterestedPerson(models.Model):
    job = models.ForeignKey(Job, default="")
    usuario = models.ForeignKey(User, default="")

    class Meta:
        unique_together = ("job", "usuario")
        verbose_name_plural = "Pessoas Interessadas"
        verbose_name = "Pessoa Interessada"

    def __str__(self):
        return "Relação de {} com {}".format(self.job.titulo_do_job, self.usuario.get_full_name())


@receiver(post_save, sender=Job)
def freela_envia_email(sender, instance, **kwargs):
    if kwargs['created']:
        if instance.empresa.email == "viniciuscarqueijo@gmail.com":
            receivers = ["viniciuscarqueijo@gmail.com"]
        else:
            receivers = [instance.empresa.email, "viniciuscarqueijo@gmail.com"]
        msg_email = empresa_cadastrou_vaga(instance.empresa, instance.titulo_do_job)
        send_mail(
            "Cadastramos sua oportunidade {} no PyJobs".format(instance.titulo_do_job),
            msg_email,
            "pyjobs@pyjobs.com.br",
            receivers)


@receiver(post_save, sender=User)
def user_criado(sender, instance, **kwargs):
    if kwargs['created']:
        send_mail("Seja bem vindo ao PyJobs",
                  user_cadastrado(instance),
                  "pyjobs@pyjobs.com.br",
                  [instance.email]
                  )


@receiver(post_save, sender=InterestedPerson)
def freelancer_envia_email(sender, instance, **kwargs):
    if kwargs['created']:
        email_pessoa = contato_cadastrado(pessoa=instance.usuario, vaga=instance.job.titulo_do_job, empresa=False)
        email_empresa = contato_cadastrado(pessoa=instance.usuario, vaga=instance.job.titulo_do_job, empresa=True)

        send_mail("PyJobs: Recebemos o seu contato!",
                  email_pessoa,
                  "pyjobs@pyjobs.com.br",
                  [instance.usuario.email]
                  )

        send_mail("PyJobs: Recebemos um interessado em sua vaga!",
                  email_empresa,
                  "pyjobs@pyjobs.com.br",
                  [instance.job.empresa.email]
                  )
