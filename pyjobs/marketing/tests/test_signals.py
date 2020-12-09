from datetime import datetime
from unittest.mock import patch, Mock
from django.conf import settings
from django.test import TestCase, override_settings
from model_mommy.recipe import Recipe

from pyjobs.marketing.triggers import (
    send_feedback_collection_email,
    send_offer_email_template,
    send_job_to_github_issues,
)
from pyjobs.marketing.models import Contact, Messages
from django.db.models.signals import post_save

from decouple import config

from pyjobs.core.models import Job, Skill


class SkillStub:
    def __init__(self):
        self.name = "Skill"


class SkillQuerySet:
    def __init__(self):
        self.skills = [SkillStub()]

    def all(self):
        return self.skills


class JobStub:
    def __init__(self):
        self.id = 1
        self.title = "Vaga 1"
        self.workplace = "Sao Paulo"
        self.company_name = "XPTO"
        self.application_link = "http://www.xpto.com.br/apply"
        self.company_email = "vm@xpto.com"
        self.description = "Job bem maneiro"
        self.issue_id = None
        self.requirements = "Requirements:\n\n\n-Fluent Python"
        self.state = 1
        self.skills = SkillQuerySet()

    def save(self):
        pass

    def get_state_display(self):
        return "São Paulo"

    def get_contract_form_display(self):
        return "CLT"


class ContactSignalTest(TestCase):
    def test_contact_signal_is_called(self):
        with patch("pyjobs.marketing.models.new_contact") as mocked_contact:
            post_save.connect(mocked_contact, sender=Contact)

        self.contact = Recipe(Contact).make()

        self.assertTrue(mocked_contact.called)


class HelpersSignalsTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = Recipe(Job, premium=True, public=True, is_challenging=True).make()

    @patch("pyjobs.marketing.triggers.send_mail")
    def test_helper_send_feedback_collection_email(self, mocked_send_mail):
        from pyjobs.marketing.models import Contact, Messages

        self.feedback_email = Recipe(Messages, message_type="feedback").make()

        send_feedback_collection_email(self.job)

        self.assertTrue(mocked_send_mail.called)

    @patch("pyjobs.marketing.triggers.send_mail")
    def test_helper_send_offer_email_template(self, mocked_send_mail):
        from pyjobs.marketing.models import Contact, Messages

        self.offer_email = Recipe(Messages, message_type="offer").make()

        send_offer_email_template(self.job)

        self.assertTrue(mocked_send_mail.called)


class GithubSignalTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.message = Messages.objects.create(
            message_title="[{workplace}] {title} @ {company_name}",
            message_content=open(
                f"{settings.PROJECT_ROOT}/marketing/tests/fixtures/message_template.md",
                "r",
            ).read(),
            message_type="github",
        )
        self.job = JobStub()

    @override_settings(GITHUB_DEFAULT_REPO="backendbr/vagas")
    @override_settings(GITHUB_ACCESS_TOKEN="access-token")
    @patch("pyjobs.marketing.triggers.Github")
    def test_if_content_is_on_message(self, _mock_github):
        send_job_to_github_issues(self.job)
        _mock_github.assert_called_once_with("access-token")
        assert _mock_github.mock_calls[1].args[0] == "backendbr/vagas"
        assert _mock_github.mock_calls[2].args[0] == "[Sao Paulo] Vaga 1 @ XPTO"
        assert len(_mock_github.mock_calls) == 3
