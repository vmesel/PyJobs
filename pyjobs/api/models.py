from django.db import models


class ApiKey(models.Model):
    api_key = models.CharField(max_length=250, null=False, blank=False)
