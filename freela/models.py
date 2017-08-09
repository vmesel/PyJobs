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
   # link_job = models.URLField(default="", blank=True, null=True)
   descricao = models.TextField(default="")
   requisitos = models.TextField(default="")
   data_adicionado = models.DateTimeField(auto_now_add=True)
   valor_pago = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
   tipo_freela = models.BooleanField(default=1) # Se for 1 eh um freela, se for 0 eh vaga
   publico = models.BooleanField(default=0)

   class Meta:
       ordering = ['-data_adicionado']

    # TODO: Adicionar campo limite de data para permitir a exclusao de um
    # freela quando acabado


class Freelancer(models.Model):
   nome = models.CharField(max_length=45, default="")
   email = models.EmailField(default="")
   portfolio = models.URLField(default="")
   job = models.ForeignKey(Freela, default="")
