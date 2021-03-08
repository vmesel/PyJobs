from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve
from model_bakery import baker as mommy
import responses
from pyjobs.core.models import Job, Profile, Skill, JobApplication
from pyjobs.core.views import index


class JobAppliedToViewTest(TestCase):
    @responses.activate
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )

        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        mommy.make("core.Skill", _quantity=7, _fill_optional=True)

        self.job.skills.set(Skill.objects.all()[:5])
        self.job.save()

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

        self.client = Client()

    def test_if_there_are_no_applications(self):
        self.client.login(username="jacob", password="top_secret")
        error_msg = "Você ainda não aplicou a nenhuma vaga via"
        response = self.client.get("/user/applied-to/")
        self.assertContains(response, error_msg)

    def test_if_the_applied_job_is_there(self):
        self.client.login(username="jacob", password="top_secret")
        JobApplication.objects.create(job=self.job, user=self.user)
        response = self.client.get("/user/applied-to/")
        self.assertContains(response, self.job.title)
