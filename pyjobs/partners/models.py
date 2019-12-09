from django.db import models
from pyjobs.core.models import Skill, Job


class Partner(models.Model):
    company_name = models.CharField("Nome da empresa", max_length=500, blank=False)
    email = models.EmailField("Email da empresa", blank=True)
    company_address = models.URLField("Site da empresa", max_length=500, blank=True)
    logo_url = models.URLField("Logo da empresa", max_length=500, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    description = models.TextField("Descrição da empresa", blank=True)
    related_jobs = models.ManyToManyField(Job, blank=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Parceiro"
