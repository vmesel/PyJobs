from unittest.mock import patch
from freezegun import freeze_time
from pyjobs.core.models import *
from django.test import TestCase
from six import StringIO
from pyjobs.core.management.commands.run_routines import Command as run_routines
from pyjobs.core.management.commands.send_weekly_summary import *
from pyjobs.core.management.commands.send_weekly_mailing import (
    check_today_is_the_right_day as check_mailing_date,
)
from model_bakery import baker as mommy
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management import call_command
import sys


class RunRoutinesTest(TestCase):
    @patch("pyjobs.core.management.commands.send_weekly_summary.post_telegram_channel")
    @patch("pyjobs.core.management.commands.send_test_reminder.Command")
    @patch("pyjobs.core.management.commands.send_weekly_mailing.Command")
    @patch("pyjobs.core.management.commands.send_weekly_summary.Command")
    def test_all_functions_are_called(
        self,
        _mocked_week_sum,
        _mocked_week_mailing,
        _mocked_test_reminder,
        _telegram_post,
    ):
        out = StringIO()
        sys.stdout = out
        call_command("run_routines", stdout=out)
        _mocked_week_sum.assert_called_once()
        _mocked_week_mailing.assert_called_once()
        _mocked_test_reminder.assert_called_once()
        self.assertEqual("True\n", out.getvalue())


class SendTestReminderTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.country = mommy.make(Country)
        self.currency = mommy.make(Currency)
        self.job = mommy.make(
            Job, public=True, country=self.country, currency=self.currency
        )
        self.profile = mommy.make(Profile, _fill_optional=True)

        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.profile.user,
            email_sent_at=datetime.now() - timedelta(days=4),
            challenge_resent=False,
            challenge_response_at=None,
        )

    def test_no_job_applying_tests(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_test_reminder", stdout=out)
        self.assertEqual("False\n", out.getvalue())

    @patch("pyjobs.core.management.commands.send_test_reminder.get_email_with_template")
    def test_changing_job_to_apply_test(self, _mocked_get_template):
        out = StringIO()
        sys.stdout = out
        self.job.is_challenging = True
        self.job.save()
        call_command("send_test_reminder", stdout=out)
        self.assertEqual("True\n", out.getvalue())
        _mocked_get_template.assert_called()
        self.job_application.refresh_from_db()
        self.assertTrue(self.job_application.challenge_resent)


class SendWeeklySummaryTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.country = mommy.make(Country)
        self.currency = mommy.make(Currency)
        self.job = mommy.make(
            Job, public=True, country=self.country, currency=self.currency
        )

    def test_formatting_string_job(self):
        self.assertEqual(
            " - {} na {} em: {} - http://www.pyjobs.com.br/job/{}".format(
                self.job.title, self.job.company_name, self.job.workplace, self.job.pk
            ),
            format_job(self.job),
        )

    def test_formatting_whole_message(self):
        self.jobs = [format_job(self.job)]
        summary_list = [
            "Olá, seja bem vindo a mais um resumo semanal de vagas do PyJobs:\n"
        ] + self.jobs
        summary_text = "\n".join(summary_list)
        self.assertEqual(summary_text, format_message_text(self.jobs))

    @freeze_time("2019-10-28")
    def test_right_date(self):
        self.assertTrue(check_today_is_the_right_day())

    @freeze_time("2019-10-29")
    def test_wrong_date(self):
        self.assertFalse(check_today_is_the_right_day())

    @freeze_time("2019-10-29")
    def test_run_command_on_wrong_date(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_weekly_summary", stdout=out)
        self.assertEqual("False\n", out.getvalue())

    @freeze_time("2019-10-28")
    def test_run_command_on_right_date(self):
        out = StringIO()
        sys.stdout = out
        call_command("send_weekly_summary", stdout=out)
        self.assertEqual("True\n", out.getvalue())
