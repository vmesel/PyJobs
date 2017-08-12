from django.db import models
from emailtools.utils import contato_prospect, email_sender
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Prospect(models.Model):
    nome = models.CharField(default="", max_length=50)
    email = models.EmailField(default="", max_length=100)
    empresa_ou_pessoa = models.BooleanField(default=False)

@receiver(post_save, sender=Prospect)
def send_email_to_prospect(sender, instance, **kwargs):
    if instance.empresa_ou_pessoa:
        email_body = contato_prospect(True, instance.nome)
    else:
        email_body = contato_prospect(False, instance.nome)
    email_sender(to_email=instance.email, from_email="viniciuscarqueijo@gmail.com",
        subject = "Coloque suas vagas para desenvolvedores Python no PyFreelas",
        content = email_body
    )
