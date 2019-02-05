from json import loads
from unittest.mock import patch

from django.shortcuts import resolve_url
from django.test import TestCase
from model_mommy import mommy

from pyjobs.core.models import Job


class TestJobResourceList(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.jobs = mommy.make(Job, _quantity=21)
        url = resolve_url('api_dispatch_list', resource_name='jobs')
        self.response = self.client.get(url)
        self.response.text = self.response.content.decode('utf-8')
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_pagination(self):
        self.assertEqual(self.response.json['meta']['limit'], 20)
        self.assertEqual(self.response.json['meta']['total_count'], 21)
        self.assertTrue(self.response.json['meta']['next'])

    def test_contents(self):
        for job in self.jobs[:20]:  # skip jobs beyond the first page
            with self.subTest():
                self.assertIn(job.company_email, self.response.text)


class TestJobResourceDetail(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(Job, _fill_optional=True)
        url = resolve_url(
            'api_dispatch_detail',
            resource_name='jobs',
            pk=self.job.pk
        )
        self.response = self.client.get(url)
        self.response.text = self.response.content.decode('utf-8')
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_contents(self):
        fields = (field.name for field in Job._meta.fields)
        for field in fields:
            if field == 'created_at':  # format dadetime as string
                self.job.created_at = str(self.job.created_at).replace(' ', 'T')

            with self.subTest():
                self.assertEqual(
                    getattr(self.job, field),
                    self.response.json[field]
                )
