from datetime import datetime, timedelta
from hashlib import sha512
from unittest.mock import patch
import responses
from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import Recipe

from pyjobs.core.models import (
    Job,
    Profile,
    JobApplication,
)
from pyjobs.marketing.triggers import (
    send_feedback_collection_email,
    send_offer_email_template,
)
from django.db.models.signals import post_save


class JobApplicationSignalTest(TestCase):
    @responses.activate
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = Recipe(Job, premium=True, public=True, is_challenging=True).make()

        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        self.user = User.objects.create_user(
            username="jacob", email="jacob@gmail.com", password="top_secret"
        )

        self.profile = Profile.objects.create(
            user=self.user,
            github="http://www.github.com/foobar",
            linkedin="http://www.linkedin.com/in/foobar",
            portfolio="http://www.foobar.com/",
            cellphone="11981435390",
        )

    def test_job_application_triggered_email(self):
        with patch(
            "pyjobs.marketing.triggers.send_email_notifing_job_application"
        ) as mocked:
            post_save.connect(mocked, sender=JobApplication)

        self.job_application = JobApplication(user=self.user, job=self.job)

        self.job_application.save()

        self.assertTrue(mocked.called)
        self.assertEqual(
            "{} applied to {}".format(self.user, self.job),
            self.job_application.__str__(),
        )
