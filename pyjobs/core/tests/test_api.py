from django.test import Client, TestCase
from unittest.mock import patch
from pyjobs.core.models import Job


class ApiRequestTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_send_group_push, _mocked_post_telegram_channel):
        self.client = Client()
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
        )
        self.job.save()

    def test_if_api_endpoint_is_available(self):
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, 200)

    def test_if_api_returns_details_from_only_job(self):
        response = self.client.get("/api/jobs/{}/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)
