from django.test import TestCase
from pyjobs.core.models import Job, Skill
from pyjobs.synchronizer.management.commands.load_jobs_from_github import *
from model_mommy import mommy
from model_mommy.recipe import Recipe

import os
from django.conf import settings

class TestLoadingJobsFromGitHub(TestCase):

    def test_if_markdown_is_parseable(self):
        sample_markdown = open(
            os.path.join(
                settings.PROJECT_ROOT,
                "synchronizer/tests/fixtures/sample_section_testing.md"
            ),
        "r")

        sections = {
            "Nossa empresa": "Bla",
            "Descrição da vaga": "Bla",
            "Local": "Bla",
            "Requisitos": "Bla",
            "Benefícios": "Bla",
            "Contratação": "Bla",
            "Como se candidatar": "Bla http://www.google.com a@b.com.br",
        }

        output = section_reshaping(sections, sample_markdown.read())

        self.assertEqual(output, sections)
    
    def test_if_markdown_is_usable_to_format_issue_content(self):
        sample_markdown = open(
            os.path.join(
                settings.PROJECT_ROOT,
                "synchronizer/tests/fixtures/sample_section_testing.md"
            ),
        "r")
        output = format_issue_content(sample_markdown.read())
        print(output)
        assert output

