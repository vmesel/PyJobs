import re

from datetime import datetime, timedelta
from pprint import pprint

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from pyjobs.core.models import Job, Skill, Country

from bs4 import BeautifulSoup as bs

from lxml import html


class Command(BaseCommand):
    jobs = []

    def get_skills_in_job(self, job_dict):
        job_dict["skills"] = []
        for skill in Skill.objects.all():
            if (
                skill.name in job_dict["requirements"]
                or skill.name in job_dict["description"]
            ):
                job_dict["skills"].append(skill)

        return job_dict

    def process_link(self, job_dict):
        """
        This function necessarily needs to retrieve the
        data available at the Python ORG website in a structured
        dictionary.
        """
        link = job_dict.pop("link")
        request = requests.get(link)
        content = request.content

        soup = bs(content, "html")

        title = soup.find("span", {"class": "company-name"}).next_element.strip()

        job_dict["description"] = " ".join(
            [
                item.__str__()
                for item in soup.find("h2", text="Job Description").find_next_siblings(
                    "p"
                )
            ]
        )

        job_dict["company_name"] = job_dict["title"].replace(f"{title},", "").strip()
        job_dict["title"] = title

        job_dict["description"] += (
            "<br>"
            + soup.find("h2", text="Restrictions").find_next_siblings("ul")[0].__str__()
        )
        job_dict["workplace"] = soup.find("span", {"class": "listing-location"}).text
        job_dict["salary_range"] = 10
        job_dict["remote"] = (
            True
            if ("remote" in job_dict["workplace"] or "Remote" in job_dict["workplace"])
            else False
        )
        try:
            job_dict["company_email"] = re.findall(
                "\S+@\S+",
                soup.find("h2", text="Restrictions")
                .find_next_siblings("ul")[1]
                .text.strip(),
            )[0]
        except:
            job_dict["company_email"] = None
        job_dict["country"] = Country.objects.get_or_create(name="Worldwide")[0]
        job_dict["issue_number"] = link.replace(
            "https://www.python.org/jobs/", ""
        ).replace("/", "")
        job_dict["job_level"] = 5

        requirements = soup.find("h2", text="Requirements").find_next_siblings()[:-2]
        requirements = [str(requirement) for requirement in requirements]

        job_dict["requirements"] = "<br>".join(requirements)
        return job_dict

    def get_all_jobs(self):
        feed = "https://www.python.org/jobs/feed/rss/"
        request = requests.get(feed)
        xml = request.content
        soup = bs(xml, "xml")

        for item in soup.findAll("item"):
            self.jobs.append(
                {
                    "title": item.select("title")[0].string,
                    "link": item.select("link")[0].string,
                }
            )

        return True

    def handle(self, *args, **options):
        self.get_all_jobs()
        for job in self.jobs:
            job_dict = self.process_link(job)

            if (
                all(
                    [
                        job_dict["description"],
                        job_dict["title"],
                        job_dict["company_name"],
                        job_dict["company_email"],
                    ]
                )
                and Job.objects.filter(issue_number=job_dict["issue_number"]).count()
                == 0
            ):
                job_dict = self.get_skills_in_job(job_dict)
                skills = job_dict.pop("skills")
                job = Job.objects.create(**job_dict)
                job.skills.set(skills)
                job.save()
