import re
from copy import copy
from datetime import datetime, timedelta
from pprint import pprint

import mistune
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Tag
from django.conf import settings
from django.core.management.base import BaseCommand
from github import Github

from pyjobs.core.models import Job, Skill

LINK_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
EMAIL_REGEX = r"[\w\.-]+@[\w\.-]+"

def section_reshaping(sections, issue_content):
    """
    This function enables markdown <h2> to be detected and inserted
    in the right section of the original dictionary.

    :params:
    sections -> Dict: this dict is a dict containing all default headers 
    issue_content -> String: this string contains the pure text of the issue
    
    :returns:
    formated_job -> Dict: it is a copy of sections that will be returned filled
    """
    formated_job = copy(sections)
    for content in issue_content.split("## "):
        for section_header in sections:
            if not content.startswith(f"{section_header}"):
                continue
            content_section_header = section_header

            if section_header in ["Nossa empresa", "Descrição da vaga"]:
                content_section_header = "Descrição da vaga"

            to_replace = f"{section_header}"
            content = content.replace(to_replace, "")
            formated_job[section_header] = str(mistune.html(content)).replace("\n", "<br/>")
    
    return formated_job


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

    formated_job = section_reshaping(sections, issue_content)

    soup = bs(formated_job["Como se candidatar"], features="html.parser")
    try:
        email = re.findall(EMAIL_REGEX, formated_job["Como se candidatar"])[0]

    except IndexError:
        email = None

    try:
        link = re.findall(
            LINK_REGEX,
            formated_job["Como se candidatar"],
        )[0][0]
    except IndexError:
        link = None

    formated_job["application_link"] = link if link else ""
    formated_job["receive_emails"] = True if email else False
    formated_job["company_email"] = email if email else settings.WEBSITE_OWNER_EMAIL

    formated_job["requirements"] = formated_job.pop("Requisitos")
    formated_job["description"] = "<br/>".join([formated_job["Nossa empresa"], formated_job["Descrição da vaga"], formated_job["Benefícios"]])


    formated_job["workplace"] = (
        bs(formated_job.pop("Local"), features="html.parser").get_text().strip()
    )
    formated_job["state"] = 27
    formated_job["cellphone"] = settings.WEBSITE_OWNER_CELLPHONE
    formated_job["ad_interested"] = False
    formated_job["challenge_interested"] = False
    formated_job["premium"] = False

    for section in sections:
        try:
            formated_job.pop(section)
        except KeyError:
            pass

    return formated_job


def setup_labels(labels, content):
    content["salary_range"] = 10
    content["contract_form"] = 1
    content["job_level"] = 5
    content["remote"] = False

    if "PJ" in labels:
        content["contract_form"] = 3
    elif "CLT" in labels:
        content["contract_form"] = 2
    elif "Estágio" in labels:
        content["contract_form"] = 4

    if "Estágiario" in labels:
        content["job_level"] = 1
    elif "Junior" in labels:
        content["job_level"] = 2
    elif "Pleno" in labels:
        content["job_level"] = 3
    elif "Senior" in labels:
        content["job_level"] = 4

    if "Remoto" in labels:
        content["remote"] = True

    skills = []

    for label in labels:
        skill, created = Skill.objects.filter(name=label).get_or_create(
            name=label
        )
        skills.append(skill)
    
    return content, skills


def setup_job_title(title, content):
    try:
        title = title.split("@")
        content["company_name"] = title[1]
        content["title"] = title[0].split("]")[1]
    except IndexError:
        pass
    return content


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
            
            if Job.objects.filter(issue_number=issue.id) or issue.user.login in self.website_managers:
                continue

            labels = [label.name for label in issue.labels]

            content = format_issue_content(issue.body)
            content = setup_job_title(issue.title, content)
            content, skills = setup_labels(labels, content)
            content["issue_number"] = issue.id

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
