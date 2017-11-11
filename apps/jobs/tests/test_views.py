from django.test import TestCase
from django.test import Client

from django.core.urlresolvers import reverse

from apps.jobs.models import Job

from model_mommy import mommy


class JobListViewTestCase(TestCase):

    def setUp(self):
        self.jobs = mommy.make(Job, _quantity=10, titulo_do_job='test')
        self.jobs_freela = mommy.make(Job, _quantity=10, titulo_do_job='test_freela')
        self.jobs_freela = mommy.make(Job, _quantity=10, titulo_do_job='test_home_office', home_office=True)
        self.url = reverse('jobs:jobs')
        self.client = Client()

    def test_view_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)

    def test_search(self):
        response = self.client.get(self.url + '?titulo=test')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)
        response = self.client.get(self.url + '?page=2&titulo=test')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)

    def test_search_freela(self):
        response = self.client.get(self.url + '?freelancer=1')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)
        response = self.client.get(self.url + '?page=2&freelancer=1')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)

    def test_search_home_office(self):
        response = self.client.get(self.url + '?home-office=1')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)
        response = self.client.get(self.url + '?page=2&home-office=1')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')
        self.assertEquals(len(response.context.get('jobs')), 5)
