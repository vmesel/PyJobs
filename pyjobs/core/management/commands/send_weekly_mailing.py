import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template import Context

from pyjobs.core.models import Job, MailingList
from pyjobs.core.utils import post_telegram_channel
from django.conf import settings


def format_owner_email(email):
    splited_email = email.split("@")
    splited_owner_email = settings.WEBSITE_OWNER_EMAIL.split("@")
    return "{}+{}@{}".format(
        splited_owner_email[0], splited_email[0], splited_owner_email[1]
    )


def check_today_is_the_right_day():
    if datetime.today().weekday() == 0:
        return True
    return False


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails_mailing_lists = [mailing.email for mailing in MailingList.objects.all()]

        if len(emails_mailing_lists) == 0:
            print("There are no mailing lists!")
            return

        emails_mailing_replies = [
            format_owner_email(email) for email in emails_mailing_lists
        ]

        to_emails = emails_mailing_replies
        from_emails = emails_mailing_lists

        jobs = list(Job.get_premium_jobs())

        missing_jobs = 10 - len(jobs)

        jobs += list(Job.get_feed_jobs())[:missing_jobs]

        if len(jobs) == 0:
            print("There are no jobs on the platform!")
            return

        plain_text = get_template("emails/weekly_summary.txt")
        html_text = get_template("emails/html/weekly_summary.html")

        subject = "PyJobs - Resumo Semanal"

        context = {
            "dono_do_site": settings.WEBSITE_OWNER_NAME,
            "nome_do_site": settings.WEBSITE_NAME,
            "url_do_site": settings.WEBSITE_HOME_URL,
            "jobs": jobs,
        }

        text_content, html_content = (
            plain_text.render(context),
            html_text.render(context),
        )

        for email_tup in zip(to_emails, from_emails):

            msg = EmailMultiAlternatives(
                subject, text_content, email_tup[1], email_tup[0]
            )
            msg.attach_alternative(html_content, "text/html")

            msg.send()

        print("Message sent!")
