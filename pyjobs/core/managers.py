from django.db import models


class PublicQuerySet(models.QuerySet):

    def public(self):
        return self.filter(public=True)
