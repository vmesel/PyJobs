from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


class Profile(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(
        "Telefone",
        max_length=16,
        validators=[
            RegexValidator(regex='^((?:\([1-9]{2}\)|\([1-9]{2}\) |[1-9]{2}|[1-9]{2} )(?:[2-8]|9[1-9])[0-9]{3}(?:\-[0-9]{4}| [0-9]{4}|[0-9]{4}))$',
            message="Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen.")]
    )
    github = models.URLField("URL do seu GitHub", default="")
    linkedin = models.URLField("URL do seu Linkedin", default="")
    portfolio = models.URLField("URL do seu Portfolio", default="")
    habilidades = models.TextField("Habilidades que você tem", default="")
    plano_de_cv_db = models.BooleanField("A conta tem acesso ao plano_de_cv_db", default=False)
    data_inscrito = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.get_full_name()


class Company(models.Model):
    usuario = models.OneToOneField(Profile)
    nome = models.CharField("Nome da empresa", max_length=45, default="")
    email = models.EmailField("Email do responsável da empresa", default="")
    site = models.URLField("Link da Empresa", default="")
    descricao = models.TextField("Descreva um pouco da empresa", default="")

    def __str__(self):
        return self.nome

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
