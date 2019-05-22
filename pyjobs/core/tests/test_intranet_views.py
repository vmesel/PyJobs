from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve
from model_mommy import mommy

from pyjobs.core.models import Job, Profile, Skill, JobApplication
from pyjobs.core.views import index


class JobAppliedToViewTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )

        mommy.make("core.Skill", _quantity=7, _fill_optional=True)

        self.job.skills = Skill.objects.all()[:5]
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
        error_msg = "Você ainda não aplicou a nenhuma vaga via PyJobs!"
        response = self.client.get("/applied-to/")
        self.assertContains(response, error_msg)


    def test_if_the_applied_job_is_there(self):
        self.client.login(username="jacob", password="top_secret")
        JobApplication.objects.create(
            job=self.job,
            user=self.user
        )
        response = self.client.get("/applied-to/")
        self.assertContains(response, self.job.title)
