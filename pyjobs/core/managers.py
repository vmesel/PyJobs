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
            created_at__lte=datetime.today(),
        )

    def created_days_ago(self, days):
        return self.filter(
            created_at__gt=datetime.today() - timedelta(days=days + 1),
            created_at__lte=datetime.today() - timedelta(days=days),
        )

    def search(self, term):
        if not term:
            return self

        params = (
            models.Q(title__icontains=term)
            | models.Q(workplace__icontains=term)
            | models.Q(description__icontains=term)
            | models.Q(requirements__icontains=term)
        )
        return self.filter(params)


class ProfilingQuerySet(models.QuerySet):
    def grade(self, skills, job_skills):
        if not skills or not job_skills:
            return 0

        intersect = set(skills) & set(job_skills)
        return (len(intersect) / len(job_skills)) * 100
