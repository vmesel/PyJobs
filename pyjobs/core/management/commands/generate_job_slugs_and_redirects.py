import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError

from pyjobs.core.models import Job


def create_job_redirect(job):
    if not job.unique_slug:
        job.generate_slug()

    for url in [
        "job_view",
        "thumbnail_view",
        "applied_users_details",
        "get_job_applications",
        "job_application_challenge_submission",
    ]:

        redirect = Redirect(
            site_id=settings.SITE_ID,
            old_path=reverse(url, kwargs={"unique_slug": job.pk}),
            new_path=reverse(url, kwargs={"unique_slug": job.unique_slug}),
        )

        redirect.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        jobs = Job.objects.filter(unique_slug=None).all()

        for job in jobs:
            create_job_redirect(job)

        return "True"
