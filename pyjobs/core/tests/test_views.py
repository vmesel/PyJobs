from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve, reverse
from model_mommy import mommy
import responses
from pyjobs.core.models import Job, Profile
from pyjobs.core.views import index


class ThumbnailTestingViews(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
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

    def test_return_thumbnail_endpoint_status_code(self):
        response = self.client.get("/thumb/{}/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)

    def test_return_signup_page_status_code(self):
        response = self.client.get("/pythonistas/signup/")
        self.assertEqual(response.status_code, 200)

    def test_return_feed_status_code(self):
        response = self.client.get("/feed/")
        self.assertEqual(response.status_code, 200)

    def test_return_register_new_job_status_code(self):
        response = self.client.get("/register/new/job/")
        self.assertEqual(response.status_code, 302)


class PyJobsSignUp(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("pyjobs.core.views.RegisterForm")
    @patch("pyjobs.core.views.login")
    def test_if_signup_page_returns_true(self, _mocked_signup_form, _mocked_login):
        response = self.client.post("/pythonistas/signup/", follow=True)
        content = response.content.decode("utf-8")
        _mocked_login.assert_called_once()


class SitemapTestingView(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
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

    def test_if_status_code_is_two_hundred_on(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(200, response.status_code)
        self.assertIn("lastmod", response.content.decode("utf-8"))


class TestingRestrictedViews(TestCase):
    @responses.activate
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        self.user = User.objects.create_user(
            username="jacob", email="jacob@gmail.com", password="top_secret"
        )

        self.profile = Profile.objects.create(
            user=self.user,
            github="http://www.github.com/foobar",
            linkedin="http://www.linkedin.com/in/foobar",
            portfolio="http://www.foobar.com/",
            cellphone="11981435390",
        )

        self.client = Client()

    def test_if_status_code_is_two_hundred_on_password_change(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/password/")
        self.assertEqual(200, response.status_code)

    def test_if_status_code_is_two_hundred_on_pythonistas_home(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/pythonistas/")
        self.assertEqual(200, response.status_code)

    def test_if_status_code_is_two_hundred_on_landing_page(self):
        response = self.client.get("/lp/landing01/")
        self.assertEqual(200, response.status_code)

    def test_if_status_code_is_two_hundred_on(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/info/")
        self.assertEqual(200, response.status_code)

    def test_if_change_password_form_is_on_page_and_validating(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.post("/password/")
        content = response.content.decode("utf-8")
        self.assertIn("Por favor, corrija os erros abaixo", content)

    @patch("pyjobs.core.views.PasswordChangeForm")
    def test_if_change_password_form_is_on_page_and_pass_changed(self, _mocked_form):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.post("/password/")
        content = response.content.decode("utf-8")
        self.assertIn("Sua senha foi alterada com sucesso!", content)

    def test_if_change_info_form_is_on_page_and_validating(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.post("/info/")
        content = response.content.decode("utf-8")
        self.assertIn("Por favor, corrija os erros abaixo", content)

    @patch("pyjobs.core.views.EditProfileForm")
    def test_if_change_info_form_is_on_page_and_info_changed(self, _mocked_form):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.post("/info/")
        content = response.content.decode("utf-8")
        self.assertIn("Suas informações foram atualizadas com sucesso!", content)
