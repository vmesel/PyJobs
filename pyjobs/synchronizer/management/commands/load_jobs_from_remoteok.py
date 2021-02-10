import re
from copy import copy
from datetime import datetime, timedelta
from pprint import pprint

import mistune
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from pyjobs.core.models import Job, Skill, Country


class Command(BaseCommand):
    def handle(self, *args, **options):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS 11.1.0; rv:42.0) Gecko/20100101 Firefox/42.0"
        }
        response = requests.get(
            f"https://remoteok.io/api?tag={settings.GITHUB_ISSUES_LABELS}",
            headers=headers,
        )
        content = response.json()
        for job in content[1:]:
            if Job.objects.filter(issue_number=job["id"]):
                continue

            new_job_data = {
                "title": job["position"],
                "company_name": job["company"],
                "description": mistune.html(job["description"]),
                "requirements": f"Click on the apply button to get to know better about this opportunity.<br/> Job from <a href='{job['apply_url']}'>RemoteOk.io</a>",
                "country": Country.objects.get_or_create(name="Worldwide")[0],
                "issue_number": job["id"],
                "remote": True,
                "job_level": 5,
                "application_link": job["apply_url"],
                "salary_range": 10,
            }

            skills = []

            for label in job["tags"]:
                skills.append(Skill.objects.get_or_create(name=label)[0])

            if all(
                [
                    new_job_data["description"],
                    new_job_data["title"],
                    new_job_data["company_name"],
                ]
            ):
                print(new_job_data)
                job = Job.objects.create(**new_job_data)
                job.skills.set(skills)
                job.save()
