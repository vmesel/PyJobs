import re
import mistune

from bs4 import BeautifulSoup as bs, NavigableString, Tag
from copy import copy
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from github import Github


def format_issue_content(issue_content):
    sections = {
        "Nossa empresa":"",
        "Descrição da vaga":"",
        "Local":"",
        "Requisitos":"",
        "Benefícios":"",
        "Contratação":"",
        "Como se candidatar":""
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
                formated_job[section_header] = f'{formated_job[section_header]}\r\n{content}'

    for key, content in formated_job.items():
        formated_job[key] = mistune.html(content)
    
    soup = bs(formated_job["Como se candidatar"])
    try:
        email = re.findall(r'[\w\.-]+@[\w\.-]+', formated_job["Como se candidatar"])[0]
    except IndexError:
        email = None
    
    try:
        link = re.findall(r"[a-z]+[:.].*?(?=\s)", formated_job["Como se candidatar"])[0]
    except IndexError:
        link = None

    formated_job["apply_link"] = link if link else None
    formated_job["apply_email"] = email if email else settings.WEBSITE_OWNER_EMAIL
    formated_job["send_email"] = True if email else False
    
    print(formated_job)




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
            state='open',
            labels=["python"],
            since=minimum_date
        )

        for issue in open_issues:
            if issue.user.login in self.website_managers:
                pass
            else:
                format_issue_content(issue.body)
                # print(issue)
            # print(issue.body)

            # print()
            # print(issue.body)
            # break
