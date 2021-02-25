from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProfilerData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    github_data = models.JSONField(_("GitHub Data"), null=True, blank=True)
    linkedin_data = models.JSONField(_("Linkedin Data"), null=True, blank=True)

    def __str__(self):
        return self.user.username

    def __repr__(self):
        return f"<ProfileData({self.user.username})>"
