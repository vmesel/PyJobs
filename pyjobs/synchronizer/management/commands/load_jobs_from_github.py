import re
import mistune

from bs4 import BeautifulSoup as bs, NavigableString, Tag
from copy import copy
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from github import Github

from pprint import pprint

from pyjobs.core.models import Skill, Job


def format_issue_content(issue_content):
    sections = {
        "Nossa empresa": "",
        "Descrição da vaga": "",
        "Local": "",
        "Requisitos": "",
        "Benefícios": "",
        "Contratação": "",
        "Como se candidatar": "",
    }
    formated_job = copy(sections)

    for content in issue_content.split("## "):
        for section_header in sections.keys():
            if content.startswith(f"{section_header}\r\n\r\n"):
                content_section_header = section_header
                if section_header in ["Nossa empresa", "Descrição da vaga"]:
                    content_section_header = "Descrição da vaga"
                to_replace = f"{section_header}\r\n\r\n"
                content = content.replace(to_replace, "")
                content = mistune.html(content)
                content = content.replace("\n", "")
                formated_job[
                    section_header
                ] = f"{formated_job[section_header]}\r\n{content}"

    for key, content in formated_job.items():
        formated_job[key] = mistune.html(content)

    soup = bs(formated_job["Como se candidatar"], features="html.parser")
    try:
        email = re.findall(r"[\w\.-]+@[\w\.-]+", formated_job["Como se candidatar"])[0]

    except IndexError:
        email = None

    try:
        link = re.findall(
            r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
            formated_job["Como se candidatar"],
        )[0][0]
    except IndexError:
        link = None

    formated_job["application_link"] = link if link else ""
    formated_job["receive_emails"] = True if email else False
    formated_job["company_email"] = email if email else settings.WEBSITE_OWNER_EMAIL

    formated_job["requirements"] = formated_job.pop("Requisitos")

    formated_job["description"] = ""
    for field in ["Nossa empresa", "Descrição da vaga", "Benefícios"]:
        if field in formated_job:
            formated_job[
                "description"
            ] = f"{formated_job['description']}<br/>{formated_job[field]}"

    formated_job["workplace"] = (
        bs(formated_job.pop("Local"), features="html.parser")
        .get_text()
        .replace("\r", "")
        .replace("\n", "")
    )
    formated_job["state"] = 27
    formated_job["cellphone"] = settings.WEBSITE_OWNER_CELLPHONE
    formated_job["ad_interested"] = False
    formated_job["challenge_interested"] = False
    formated_job["premium"] = False

    for section in sections.keys():
        try:
            formated_job.pop(section)
        except KeyError:
            pass

    return formated_job


class Command(BaseCommand):
    def __init__(self):
        self.website_managers = settings.WEBSITE_MANAGERS_GITHUB_NICKNAME.split(",")

    def handle(self, *args, **options):
        if not settings.GITHUB_ACCESS_TOKEN or not settings.GITHUB_DEFAULT_REPO:
            return "False"

        g = Github(settings.GITHUB_ACCESS_TOKEN)
        repo = g.get_repo(settings.GITHUB_DEFAULT_REPO)

        minimum_date = datetime.now() - timedelta(days=30)

        open_issues = repo.get_issues(
            state="open", labels=["python"], since=minimum_date
        )

        for issue in open_issues:
            if Job.objects.filter(issue_number=issue.id):
                continue

            if issue.user.login in self.website_managers:
                continue

            content = format_issue_content(issue.body)
            content["issue_number"] = issue.id
            try:
                title = issue.title.split("@")
                content["company_name"] = title[1]
                content["title"] = title[0].split("]")[1]
            except IndexError:
                continue

            labels = [label.name for label in issue.labels]

            content["salary_range"] = 10

            if "PJ" in labels:
                content["contract_form"] = 3
            elif "CLT" in labels:
                content["contract_form"] = 2
            elif "Estágio" in labels:
                content["contract_form"] = 4
            else:
                content["contract_form"] = 1

            if "Estágiario" in labels:
                content["job_level"] = 1
            elif "Junior" in labels:
                content["job_level"] = 2
            elif "Pleno" in labels:
                content["job_level"] = 3
            elif "Senior" in labels:
                content["job_level"] = 4
            else:
                content["job_level"] = 5

            if "Remoto" in labels:
                content["remote"] = True
            else:
                content["remote"] = False

            skills = []

            for label in labels:
                if skill := Skill.objects.filter(name=label).first():
                    skills.append(skill)
                else:
                    skill = Skill.objects.create(name=label)
                    skills.append(skill)

            if (
                content["description"] == ""
                or content["requirements"] == ""
                or content["description"] is None
                or content["requirements"] is None
            ):
                continue

            job = Job.objects.create(**content)
            job.skills.set(skills)
            job.save()
