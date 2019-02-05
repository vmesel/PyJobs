from json import loads
from unittest.mock import patch

from django.shortcuts import resolve_url
from django.test import TestCase
from model_mommy import mommy

from pyjobs.api.views import JobResource
from pyjobs.core.models import Job


PER_PAGE = JobResource.page_size


class TestJobResourceList(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.jobs = mommy.make(Job, _quantity=PER_PAGE + 1, public=True)
        mommy.make(Job, public=False)
        url = resolve_url('api:job_list')
        self.response = self.client.get(url)
        self.response.text = self.response.content.decode('utf-8')
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_pagination(self):
        self.assertEqual(self.response.json['meta']['limit'], PER_PAGE)
        self.assertEqual(self.response.json['meta']['total_count'], PER_PAGE + 2)
        self.assertTrue(self.response.json['meta']['next'])

    def test_contents(self):
        for job in self.jobs[PER_PAGE:]:  # skip jobs beyond the first page
            with self.subTest():
                self.assertIn(job.company_email, self.response.text)


class TestJobResourceDetail(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.job = mommy.make(Job, _fill_optional=True, public=True)
        url = resolve_url('api:job_detail', pk=self.job.pk)
        self.response = self.client.get(url)
        self.response.text = self.response.content.decode('utf-8')
        self.response.json = loads(self.response.text)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_contents(self):
        fields = (
            field.name for field in Job._meta.fields
            if field.name not in {'premium', 'public', 'ad_interested'}
        )
        for field in fields:
            if field == 'created_at':  # format dadetime as string
                self.job.created_at = str(self.job.created_at).replace(' ', 'T')

            with self.subTest():
                self.assertEqual(
                    getattr(self.job, field),
                    self.response.json[field]
                )
