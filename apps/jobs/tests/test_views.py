from django.test import TestCase
from django.test import Client

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.jobs.models import Job

from model_mommy import mommy


class JobListViewTestCase(TestCase):

    def setUp(self):
        self.jobs = mommy.make(Job, _quantity=10)
        self.url = reverse('jobs:jobs')
        self.client = Client()

    def test_view_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
