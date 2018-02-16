from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User

from apps.core.models import Company
from apps.emailtools.utils import empresa_cadastrou_vaga, contato_cadastrado, user_cadastrado, vaga_publicada

import telegram
from decouple import config


class Job(models.Model):

    NIVEL_CHOICES = (
        ('junior', 'Júnior'),
        ('pleno', 'Pleno'),
        ('senior', 'Sênior'),
    )

    titulo_do_job = models.CharField("Título do job", max_length=100, default="")
    empresa = models.ForeignKey(Company)
    home_office = models.BooleanField("Aceita home office", default=False)
    descricao = models.TextField("Descrição do job", default="")
    requisitos = models.TextField("Requisitos para o Job", default="")
    data_adicionado = models.DateTimeField("Data que o job foi adicionado", auto_now_add=True)
    local = models.CharField("Local da vaga", max_length=100, default="",
                             help_text="Preencha com o lugar da vaga, caso seja remota, explicite!")
    tipo_freela = models.BooleanField("O job é freela?", default=1,
                                      help_text="Selecione apenas se o job for para freelancers")
    publico = models.BooleanField("Este job é público?", default=0)
    nivel = models.CharField("Nível", max_length=30, choices=NIVEL_CHOICES)
    __original_public = False

    class Meta:
        verbose_name = 'Vaga'
        verbose_name_plural = 'Vagas'
        ordering = ['-data_adicionado']

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__original_public = self.publico

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.__original_public == 0:
            if self.publico != self.__original_public:
                bot = telegram.Bot(config("TELEGRAM_TOKEN"))
                message_text = "Nova oportunidade! {job} - {empresa} em {local}\n http://www.pyjobs.com.br/job/{link}/".format(
                    job=self.titulo_do_job,
                    empresa=self.empresa,
                    local=self.local,
                    link=self.pk
                )
                bot.send_message(chat_id = config("TELEGRAM_CHATID"), text=message_text)
                bot.send_message(chat_id = "@pythonbrasil", text=message_text)
                msg_email = vaga_publicada(empresa=self.empresa.nome, vaga=self.titulo_do_job, pk=self.pk)
                receivers = [self.empresa.email]
                send_mail(
                    "Sua oportunidade está disponível no PyJobs",
                    msg_email,
                    "pyjobs@pyjobs.com.br",
                    receivers)


        super(Job, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_public = self.publico


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
