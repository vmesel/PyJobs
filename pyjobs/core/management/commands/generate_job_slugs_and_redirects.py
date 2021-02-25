import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.conf import settings
from django.db import IntegrityError

from pyjobs.core.models import Job


class Command(BaseCommand):
    def handle(self, *args, **options):
        jobs = Job.objects.filter(unique_slug=None).all()

        for job in jobs:
            slug = job.generate_slug()

            redirect = Redirect.objects.create(
                site_id=settings.SITE_ID,
                old_path=f"/job/{job.id}/",
                new_path=f"/job/{job.unique_slug}/",
            )

            redirect.save()

        return "True"
