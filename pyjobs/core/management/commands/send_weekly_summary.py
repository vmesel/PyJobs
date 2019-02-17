import os

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from pyjobs.core.models import Job
from pyjobs.core.utils import post_telegram_channel


def format_job(job):
    return " - {} na {} em: {} - http://www.pyjobs.com.br/job/{}".format(
        job.title, job.company_name, job.workplace, job.pk
    )


def format_message_text(jobs):
    summary_list = [
        "Olá, seja bem vindo a mais um resumo semanal de vagas do PyJobs:\n"
    ]
    summary_list += jobs
    return "\n".join(summary_list)


def check_today_is_the_right_day():
    if datetime.today().weekday() == 0:
        return True
    return False


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not check_today_is_the_right_day():
            print("Today is not the right day!")
            return False

        jobs = list(Job.get_premium_jobs())

        missing_jobs = 10 - len(jobs)

        jobs += list(Job.get_feed_jobs())[:missing_jobs]

        formated_jobs = [format_job(job) for job in jobs]

        post_telegram_channel(format_message_text(formated_jobs))

        print("Message sent!")
        return True
