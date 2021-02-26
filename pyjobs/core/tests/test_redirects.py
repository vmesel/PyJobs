from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse
from django.contrib.redirects.models import Redirect
from django.conf import settings
from model_bakery import baker as mommy
import responses
import json
from datetime import datetime, timedelta
from pyjobs.core.models import Job, Profile, JobApplication
from pyjobs.core.views import index, jobs
from pyjobs.core.forms import JobApplicationForm
import csv
import io


class RedirectTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
        )
        self.job.save()
        self.client = Client()

        self.job_old_url = reverse("job_view", kwargs={"unique_slug": self.job.pk})
        self.job_new_url = reverse(
            "job_view", kwargs={"unique_slug": self.job.unique_slug}
        )

    def test_if_redirect_exists(self):
        response = self.client.get(self.job_old_url, follow=True)
        self.assertEquals(response.redirect_chain[0][0], self.job_new_url)
        self.assertEquals(response.redirect_chain[0][1], 301)
