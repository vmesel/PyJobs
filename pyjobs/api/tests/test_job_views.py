from json import loads
from unittest.mock import patch

from django.shortcuts import resolve_url
from django.test import TestCase, Client
from model_bakery import baker as mommy

from pyjobs.api.views import JobResource
from pyjobs.core.models import Job, Country, Currency

PER_PAGE = JobResource.page_size


class TestJobResourceList(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.country = mommy.make(Country)
        self.currency = mommy.make(Currency)
        self.client = Client()
        self.jobs = mommy.make(
            Job,
            _quantity=PER_PAGE * 3,
            public=True,
            country=self.country,
            currency=self.currency,
        )
        mommy.make(Job, public=False)
        self.url = resolve_url("api:job_list")
        self.response = self.client.get(self.url)
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_pagination(self):
        self.assertEqual(self.response.json["meta"]["limit"], PER_PAGE)
        self.assertEqual(self.response.json["meta"]["total_count"], PER_PAGE * 3 + 1)
        self.assertTrue(self.response.json["meta"]["next"])

    def test_if_holds_errors(self):
        self.response = self.client.get(self.url + "?page=1000")
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)
        self.assertEqual(400, self.response.status_code)
        self.assertTrue(self.response.json["error"])
        self.assertEqual(self.response.json["error"], "Invalid page number")


class TestJobResourceListIfEmpty(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.url = resolve_url("api:job_list")
        self.response = self.client.get(self.url)
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_response_status_code(self):
        self.assertEqual(200, self.response.status_code)
        self.assertEqual([], self.response.json["objects"])


class TestJobResourceDetail(TestCase):
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
        self.client = Client()
        url = resolve_url("api:job_detail", pk=self.job.pk)
        self.response = self.client.get(url)
        self.response.text = self.response.content.decode("utf-8")
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_contents(self):
        fields = (
            field.name
            for field in Job._meta.fields
            if field.name
            in {
                "id",
                "title",
                "workplace",
                "company_name",
                "description",
                "requirements",
                "created_at",
                "remote",
            }
        )
        for field in fields:
            if field == "created_at":  # format datetime as string
                self.job.created_at = self.job.created_at.strftime("%Y-%m-%d %H:%M:%S")

            with self.subTest():
                self.assertEqual(getattr(self.job, field), self.response.json[field])
