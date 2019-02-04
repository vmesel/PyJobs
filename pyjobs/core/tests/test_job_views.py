from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import resolve

from pyjobs.core.models import Job, Profile
from pyjobs.core.views import index


class HomeJobsViewsTest(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
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

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
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
        self.job_view_html = self.client.get(f"/job/{self.job.pk}/")\
            .content.decode('utf-8')

    def test_job_title_in_view(self):
        self.assertTrue(self.job.title in self.job_view_html)

    def test_job_workplace_in_view(self):
        self.assertTrue(self.job.workplace in self.job_view_html)

    def test_job_company_in_view(self):
        self.assertTrue(self.job.company_name in self.job_view_html)

    def test_job_application_link_in_view(self):
        self.assertTrue(self.job.application_link in self.job_view_html)

    def test_job_description_in_view(self):
        self.assertTrue(self.job.description in self.job_view_html)

    def test_job_requirements_in_view(self):
        self.assertTrue(self.job.requirements in self.job_view_html)


class PyJobsJobApplication(TestCase):

    @patch('pyjobs.core.models.post_telegram_channel')
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True
        )

        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@gmail.com',
            password='top_secret'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            github="http://www.github.com/foobar",
            linkedin="http://www.linkedin.com/in/foobar",
            portfolio="http://www.foobar.com/",
            cellphone="11981435390"
        )

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
