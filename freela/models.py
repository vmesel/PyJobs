from __future__ import unicode_literals

from django.db import models


# A ser implementado em um futuro, por ser mais complexo
class Empresa(models.Model):
    pass


class Freela(models.Model):
   empresa = models.CharField(max_length=45, default="")
   email_responsavel_empresa = models.EmailField(default="")
   link_da_empresa = models.URLField(default="")
   titulo_do_job = models.CharField(max_length=100, default="")
   link_job = models.URLField(default="", blank=True, null=True)
   descricao = models.TextField(default="")
   requisitos = models.TextField(default="")
   data_adicionado = models.DateTimeField(auto_now_add=True)

   class Meta:
       ordering = ['-data_adicionado']

    # TODO: Adicionar campo limite de data para permitir a exclusao de um
    # freela quando acabado


# A ser implementado em um futuro, por ser mais complexo
class Freelancer(models.Model):
    pass
