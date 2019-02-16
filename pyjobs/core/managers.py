from datetime import datetime, timedelta

from django.db import models


class PublicQuerySet(models.QuerySet):

    def public(self):
        return self.filter(public=True)

    def premium(self):
        return self.public().filter(premium=True)

    def not_premium(self):
        return self.public().filter(premium=False)

    def created_in_the_last(self, days):
        return self.filter(
            created_at__gt=datetime.today() - timedelta(days=days),
            created_at__lte=datetime.today()
        )

    def search(self, term):
        if not term:
            return self

        params = (
            models.Q(title__icontains=term) |
            models.Q(workplace__icontains=term) |
            models.Q(description__icontains=term) |
            models.Q(requirements__icontains=term)
        )
        return self.filter(params)
