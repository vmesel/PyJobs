from django.test import TestCase
from pyjobs.core.models import Job, Skill
from pyjobs.synchronizer.management.commands.load_jobs_from_github import *
from model_bakery import baker as mommy
from model_mommy.recipe import Recipe

import os
from django.conf import settings


class ExampleLabel:
    def __init__(self, name):
        self.name = name


class ExampleIssue:
    def __init__(self, body, labels, title):
        self._body = body
        self._title = title
        self._labels = [ExampleLabel(label) for label in labels]

    @property
    def body(self):
        return self._body

    @property
    def labels(self):
        return self._labels

    @property
    def title(self):
        return self._title


class TestLoadingJobsFromGitHub(TestCase):
    def setUp(self):
        self.sample_markdown = open(
            os.path.join(
                settings.PROJECT_ROOT,
                "synchronizer/tests/fixtures/sample_section_testing.md",
            ),
            "r",
        ).read()
        self.labels = ["Pleno", "AWS", "CLI", "Remoto"]
        self.issue = ExampleIssue(
            self.sample_markdown, self.labels, "[REMOTO] Dev Pleno @ PyJobs"
        )

    def test_if_markdown_is_parseable(self):
        sections = {
            "Nossa empresa": "<p>Bla</p><br/>",
            "Descrição da vaga": "<p>Bla<br/>Bla<br/>Bla<br/>Bla<br/>Bla</p><br/>",
            "Local": "<p>Bla</p><br/>",
            "Requisitos": "<p>Bla</p><br/>",
            "Benefícios": "<p>Bla</p><br/>",
            "Contratação": "<p>Bla</p><br/>",
            "Como se candidatar": "<p>Bla http://www.google.com a@b.com.br</p><br/>",
        }

        output = section_reshaping(sections, self.sample_markdown)
        self.assertEqual(output, sections)

    def test_if_markdown_is_usable_to_format_issue_content(self):
        output = format_issue_content(self.sample_markdown)
        expected = {
            "application_link": "http://www.google.com",
            "receive_emails": True,
            "company_email": "a@b.com.br",
            "requirements": "<p>Bla</p><br/>",
            "description": "<p>Bla</p><br/><br/><p>Bla<br/>Bla<br/>Bla<br/>Bla<br/>Bla</p><br/><br/><p>Bla</p><br/>",
            "workplace": "Bla",
            "state": 27,
            "cellphone": None,
            "ad_interested": False,
            "challenge_interested": False,
            "premium": False,
        }
        assert output == expected

    def test_if_labels_are_being_detected_right(self):
        content = format_issue_content(self.issue.body)
        content = setup_job_title(self.issue.title, content)
        content, skills = setup_labels(self.labels, content)

        assert len(skills) > 0
        assert isinstance(content, dict)
        assert content["job_level"] == 3
        assert content["contract_form"] == 1
        assert content["remote"] == True
