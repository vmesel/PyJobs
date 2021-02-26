from unittest.mock import patch
from pyjobs.core.models import Skill
from django.test import TestCase, override_settings
from freezegun import freeze_time
from six import StringIO
from pyjobs.core.models import Job
from pyjobs.marketing.models import Messages, MailingList
from datetime import datetime, timedelta
from pyjobs.core.management.commands.send_weekly_mailing import *
from django.core.management import call_command
from model_bakery import baker as mommy
import sys


class FeedbackRequestTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = mommy.make(
            Job, created_at=datetime.now() - timedelta(14), premium=True
        )
        self.mailing_list = MailingList.objects.create(
            email="list@pyjobs.com.br", name="pyjobs", slug="pyjobs"
        )
        mommy.make(Messages, message_type="feedback")
        self.job.premium_at = datetime.now() - timedelta(14)
        self.job.save()

    @override_settings(WEBSITE_OWNER_EMAIL="pyjobstest@pyjobs.com.br")
    def test_format_owner_email(self):
        formatted_email = format_owner_email(self.mailing_list.email)
        self.assertEqual(formatted_email, "pyjobstest+list@pyjobs.com.br")

    @freeze_time("2019-10-30")
    def test_right_date(self):
        self.assertTrue(check_today_is_the_right_day())

    @freeze_time("2019-10-29")
    def test_wrong_date(self):
        self.assertFalse(check_today_is_the_right_day())

    @freeze_time("2019-10-29")
    def test_called_command_with_wrong_date(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_weekly_mailing", stdout=out)
        self.assertEqual("False\n", out.getvalue())


class FeedbackRequestWithNoMailingListTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        mommy.make(Job, public=True, created_at=datetime.now() - timedelta(5))

    @freeze_time("2019-10-29")
    def test_called_command_with_no_jobs_wrong_date(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_weekly_mailing", stdout=out)
        self.assertEqual("False\n", out.getvalue())


class FeedbackRequestWithNoJobsTest(TestCase):
    def setUp(self):
        self.mailing_list = MailingList.objects.create(
            email="list@pyjobs.com.br", name="pyjobs", slug="pyjobs"
        )

    @freeze_time("2019-10-29")
    def test_called_command_with_no_jobs_wrong_date(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_weekly_mailing", stdout=out)
        self.assertEqual("False\n", out.getvalue())
