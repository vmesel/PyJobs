from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve, reverse
from model_mommy import mommy

from pyjobs.core.models import Job, Profile
from pyjobs.core.views import index


class ThumbnailTestingViews(TestCase):
    def setUp(self):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            requirements="Job bem maneiro",
        )
        self.job.save()
        self.client = Client()

    def test_return_thumbnail_endpoint_status_code(self):
        response = self.client.get("/thumb/{}/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)

    def test_return_signup_page_status_code(self):
        response = self.client.get("/pythonistas/signup/")
        self.assertEqual(response.status_code, 200)

    def test_return_jooble_feed_status_code(self):
        response = self.client.get("/jooble/")
        self.assertEqual(response.status_code, 200)

    def test_return_feed_status_code(self):
        response = self.client.get("/feed/")
        self.assertEqual(response.status_code, 200)

    def test_return_register_new_job_status_code(self):
        response = self.client.get("/register/new/job/")
        self.assertEqual(response.status_code, 302)
