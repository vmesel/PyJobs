import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template import Context

from pyjobs.core.models import Job, JobApplication
from pyjobs.core.email_utils import get_email_with_template
from django.conf import settings
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        job_qs = Job.objects.filter(is_challenging=True)

        if len(job_qs) == 0:
            return "False"

        for job in job_qs:
            job_applications = JobApplication.objects.filter(
                job=job,
                challenge_response_at=None,
                email_sent_at__gte=datetime.now() - timedelta(days=5),
                email_sent_at__lte=datetime.now() + timedelta(days=3),
                challenge_resent=False,
            )

            for job_app in job_applications:
                person_email_context = {
                    "vaga": job,
                    "pessoa": job_app.user.profile,
                    "mensagem": job_app,
                }
                template_person = "job_interest_challenge"
                person_email_subject = (
                    "Reenviando: Teste Técnico da empresa: {}!".format(job.company_name)
                )

                job_app.challenge_resent = True
                job_app.save()

                msg_email_person = get_email_with_template(
                    template_person,
                    person_email_context,
                    person_email_subject,
                    (job_app.user.email,),
                )
                msg_email_person.send()

        return "True"
