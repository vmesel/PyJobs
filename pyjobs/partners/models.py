from django.db import models
from pyjobs.core.models import Skill, Job
from django.utils.translation import gettext_lazy as _


class Partner(models.Model):
    company_name = models.CharField(_("Nome da empresa"), max_length=500, blank=False)
    email = models.EmailField(_("Email da empresa"), blank=True)
    company_address = models.URLField(_("Site da empresa"), max_length=500, blank=True)
    logo_url = models.URLField(_("Logo da empresa"), max_length=500, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    description = models.TextField(_("Descrição da empresa"), blank=True)
    related_jobs = models.ManyToManyField(Job, blank=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = _("Parceiro")
