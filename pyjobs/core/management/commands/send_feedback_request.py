import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from pyjobs.core.models import Job, send_feedback_collection_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        jobs = Job.get_jobs_to_get_feedback()

        for job in jobs:
            send_feedback_collection_email(job)

        print("Message sent!")
