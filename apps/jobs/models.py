from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core.mail import send_mail
from apps.emailtools.utils import empresa_cadastrou_vaga, contato_cadastrado


class Job(models.Model):
   empresa = models.CharField("Nome da empresa", max_length=45, default="")
   email_responsavel_empresa = models.EmailField("Email do responsável", default="")
   link_da_empresa = models.URLField("Link da Empresa", default="")
   titulo_do_job = models.CharField("Título do job", max_length=100, default="")
   descricao = models.TextField("Descrição do job", default="")
   requisitos = models.TextField("Requisitos para o Job", default="")
   data_adicionado = models.DateTimeField("Data que o job foi adicionado", auto_now_add=True)
   # data_limite =  models.DateTimeField("Data que o job foi adicionado", auto_now_add=True)
   tipo_freela = models.BooleanField("O job é freela?", default=1, help_text="Selecione apenas se o job for para freelancers") # Se for 1 eh um freela, se for 0 eh vaga
   publico = models.BooleanField("Este job é público?", default=0)
   local = models.CharField("Local da vaga", max_length=100, default="Não Especificado", help_text="Preencha com o lugar da vaga, caso seja remota, explicite!")

   class Meta:
       ordering = ['-data_adicionado']
       db_table = 'freela_freela'


class Person(models.Model):
   nome = models.CharField(max_length=45, default="")
   email = models.EmailField(default="")
   portfolio = models.URLField(default="")
   job = models.ForeignKey(Job, default="")
   data_inscrito = models.DateTimeField(auto_now_add=True)

   class Meta:
       db_table = "freela_freelancer"


@receiver(post_save, sender=Job)
def freela_envia_email(sender, instance, **kwargs):
    if kwargs['created']:
        msg_email = empresa_cadastrou_vaga(instance.empresa, instance.titulo_do_job)
        send_mail("Cadastramos sua oportunidade {} no PyJobs".format(instance.titulo_do_job),
                msg_email,
                "pyjobs@pyjobs.com.br",
                [instance.email_responsavel_empresa, "viniciuscarqueijo@gmail.com"])


@receiver(post_save, sender=Person)
def freelancer_envia_email(sender, instance, **kwargs):
        if kwargs['created']:
            email_pessoa = contato_cadastrado(nome = instance.nome, email = instance.email, portfolio = instance.portfolio, vaga=instance.job.titulo_do_job, empresa=False)
            email_empresa = contato_cadastrado(nome = instance.nome, email = instance.job.email_responsavel_empresa, portfolio = instance.portfolio, vaga=instance.job.titulo_do_job, empresa=True)

            send_mail("PyJobs: Recebemos o seu contato!",
                        email_pessoa,
                        "pyjobs@pyjobs.com.br",
                        [instance.email]
                        )

            send_mail("PyJobs: Recebemos um interessado em sua vaga!",
                        email_empresa,
                        "pyjobs@pyjobs.com.br",
                        [instance.job.email_responsavel_empresa]
                        )
