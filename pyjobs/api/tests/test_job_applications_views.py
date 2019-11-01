from json import loads
from unittest.mock import patch

from django.shortcuts import resolve_url
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import Recipe

from pyjobs.api.views import JobResource
from pyjobs.core.models import Job, JobApplication, Profile
from pyjobs.api.models import ApiKey


class TestJobApplicationResourceList(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(Job, _fill_optional=True, public=True)
        self.api_key = mommy.make(ApiKey)
        url = resolve_url("api:jobapplication_list")
        self.response = self.client.get(
            "{}?id={}&api_key={}".format(url, self.job.pk, self.api_key.api_key)
        )
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_noresults(self):
        self.assertEqual(len(self.response.json["objects"]), 0)


class TestJobApplicationResourceListWithInvalidAPIKey(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(Job, _fill_optional=True, public=True)
        self.api_key = mommy.make(ApiKey)
        url = resolve_url("api:jobapplication_list")
        self.response = self.client.get(
            "{}?id={}&api_key={}".format(
                url, self.job.pk, self.api_key.api_key + "test"
            )
        )
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_error_status(self):
        self.assertEqual(401, self.response.status_code)
        self.assertTrue("error" in self.response.json)


class TestJobApplicationWithItemsResourceList(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(Job)
        self.profile = mommy.make(Profile)

        self.job_app = JobApplication.objects.create(
            user=self.profile.user, job=self.job
        )

        self.api_key = mommy.make(ApiKey)
        url = resolve_url("api:jobapplication_list")
        self.response = self.client.get(
            "{}?id={}&api_key={}".format(url, self.job_app.job.pk, self.api_key.api_key)
        )
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_results(self):
        self.assertEqual(len(self.response.json["objects"]), 1)
