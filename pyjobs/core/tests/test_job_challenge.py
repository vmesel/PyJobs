from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve, reverse
from model_mommy import mommy
import responses
from pyjobs.core.models import Job, Profile, JobApplication
from pyjobs.core.views import index
import datetime


class TestingRestrictedViews(TestCase):
    @responses.activate
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(
            "core.Job", is_challenging=True, challenge="Ola mundo dos testes"
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

        self.client = Client()

        self.client.login(username="jacob", password="top_secret")

    def test_if_user_is_not_applied_to_job(self):
        response = self.client.get("/job/{}".format(self.job.pk), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(b"Candidate-se para esta vaga pelo" in response.content)

    def test_if_applied_user_can_get_job_challenge(self):
        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.user,
            email_sent=True,
            email_sent_at=datetime.datetime.now(),
        )
        response = self.client.get("/job/{}".format(self.job.pk), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(b"Clique aqui e preencha o desafio" in response.content)

    def test_if_applied_user_can_answer_job_challenge(self):
        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.user,
            email_sent=True,
            email_sent_at=datetime.datetime.now(),
        )
        response = self.client.get(
            "/job/{}/challenge_submit/".format(self.job.pk), follow=True
        )

    def test_if_applied_user_cant_answer_job_challenge(self):
        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.user,
            email_sent=True,
            email_sent_at=datetime.datetime.now(),
            challenge_response_at=datetime.datetime.now(),
            challenge_response_link="http://www.google.com",
        )
        response = self.client.get(
            "/job/{}/challenge_submit/".format(self.job.pk), follow=True
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            bytes("Recebemos seu teste, aguarde nosso retorno!", "utf8")
            in response.content
        )
