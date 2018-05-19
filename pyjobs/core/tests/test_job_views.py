from django.urls import resolve
from django.http import HttpRequest
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser

from core.views import *
from core.models import Job

class HomeJobsViewsTest(TestCase):
    def setUp(self):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link = "http://www.xpto.com.br/apply",
            company_email = "vm@xpto.com",
            description="Job bem maneiro"
        )
        self.job.save()
        self.home_page = resolve('/')
        self.request = HttpRequest()
        self.home_page_html = index(self.request).content.decode('utf-8')

    def test_job_is_in_websites_home(self):
        self.assertEqual(self.home_page.func, index)

    def test_job_in_home(self):
        job_title = str(self.job)
        self.assertTrue(job_title in self.home_page_html)

    def test_job_url_is_in_home(self):
        job_url = "/job/{}/".format(str(self.job.pk))
        self.assertTrue(job_url in self.home_page_html)


class JobDetailsViewTest(TestCase):
    def setUp(self):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link = "http://www.xpto.com.br/apply",
            company_email = "vm@xpto.com",
            description="Job bem maneiro",
            requirements="Job bem maneiro",
        )
        self.job.save()
        self.job_request = HttpRequest()
        self.job_view_html = job_view(self.job_request, self.job.pk)\
            .content.decode('utf-8')

    def test_job_details_view(self):
        self.assertTrue(self.job.title in self.job_view_html)
        self.assertTrue(self.job.workplace in self.job_view_html)
        self.assertTrue(self.job.company_name in self.job_view_html)
        self.assertTrue(self.job.application_link in self.job_view_html)
        self.assertTrue(self.job.description in self.job_view_html)
        self.assertTrue(self.job.requirements in self.job_view_html)


class PyJobsJobApplication(TestCase):
    def setUp(self):
        self.job = Job(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email = "vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True
        )
        self.job.save()
        self.user = User.objects.create_user(
                username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client = Client()

    def test_check_applied_for_job_anon(self):
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode('utf-8')
        expected_response = "Você precisa estar logado para aplicar para esta vaga!"
        self.assertTrue(expected_response in request)

    def test_check_applied_for_job(self):
        self.client.login(username="jacob", password="top_secret")
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode('utf-8')
        expected_response = "Aplicar para esta vaga pelo PyJobs"
        self.assertTrue(expected_response in request)
