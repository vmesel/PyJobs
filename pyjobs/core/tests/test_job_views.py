from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse
from model_mommy import mommy
import responses
import json
from datetime import datetime
from pyjobs.core.models import Job, Profile, JobApplication
from pyjobs.core.views import index, jobs
from pyjobs.core.forms import JobApplicationForm
import csv
import io


class HomeJobsViewsTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
        )
        self.job.save()
        self.jobs_page = resolve("/jobs/")
        self.home_page = resolve("/")
        self.request = HttpRequest()
        self.home_page_html = index(self.request).content.decode("utf-8")
        self.jobs_page_html = jobs(self.request).content.decode("utf-8")

    def test_job_is_in_websites_home(self):
        self.assertEqual(self.home_page.func, index)

    def test_job_in_home(self):
        job_title = self.job.title
        self.assertTrue(job_title in self.jobs_page_html)

    def test_job_url_is_in_home(self):
        job_url = "/job/{}/".format(str(self.job.pk))
        self.assertTrue(job_url in self.jobs_page_html)


class JobDetailsViewTest(TestCase):
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
        self.job_view_html = self.client.get(f"/job/{self.job.pk}/").content.decode(
            "utf-8"
        )

    def test_job_title_in_view(self):
        self.assertTrue(self.job.title in self.job_view_html)

    def test_job_workplace_in_view(self):
        self.assertTrue(self.job.workplace in self.job_view_html)

    def test_job_company_in_view(self):
        self.assertTrue(self.job.company_name in self.job_view_html)

    def test_job_application_link_not_in_view(self):
        self.assertTrue(self.job.application_link not in self.job_view_html)

    def test_job_description_in_view(self):
        self.assertTrue(self.job.description in self.job_view_html)

    def test_job_requirements_in_view(self):
        self.assertTrue(self.job.requirements in self.job_view_html)


class PyJobsJobApplication(TestCase):
    @responses.activate
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
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

    def test_check_applied_for_job_anon(self):
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode("utf-8")
        expected_response = "Se logue e aplique a vaga!"
        self.assertTrue(expected_response in request)

    def test_check_applied_for_job(self):
        self.client.login(username="jacob", password="top_secret")
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode("utf-8")
        expected_response = "Candidate-se para esta vaga pelo"
        self.assertTrue(expected_response in request)

    def test_check_if_profile_with_no_skills_can_apply(self):
        self.client.login(username="jacob", password="top_secret")
        job_url = "/job/{}/".format(self.job.pk)
        request_client = self.client.get(job_url)
        request = request_client.content.decode("utf-8")
        request_apply = self.client.post(job_url, follow=True)

        self.assertTrue(
            "Você já aplicou a esta vaga!" in request_apply.content.decode("utf-8")
        )


class PyJobsContact(TestCase):
    def setUp(self):
        self.client = Client()

    def test_check_if_is_correct_page(self):
        response = self.client.get("/contact/").content.decode("utf-8")
        self.assertTrue("Contato" in response)

    @override_settings(RECAPTCHA_SECRET_KEY="my-secret")
    def test_check_if_is_validating_the_form(self):
        response = self.client.post("/contact/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Falha na hora de mandar a mensagem" in content)

    @override_settings(RECAPTCHA_SECRET_KEY=None)
    @patch("pyjobs.core.views.ContactForm")
    @responses.activate
    def test_check_if_when_recaptcha_is_none_message_is_sent(self, _mocked_form_save):
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": "Success"},
            status=200,
        )
        response = self.client.post("/contact/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Mensagem enviada com sucesso" in content)


class PyJobsMultipleJobsPagesTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make("core.Job", _quantity=14)
        self.client = Client()

    def test_first_page(self):
        response = self.client.get("/jobs/?page=1")
        self.assertTrue(response.status_code == 200)

    def test_second_page(self):
        response = self.client.get("/jobs/?page=2")
        self.assertTrue(response.status_code == 200)

    def test_third_page_redirection(self):
        response = self.client.get("/jobs/?page=3")
        self.assertRedirects(response, "/", status_code=302, target_status_code=200)

    def test_string_in_page_redirection(self):
        response = self.client.get("/jobs/?page=ola")
        self.assertRedirects(response, "/", status_code=302, target_status_code=200)


class PyJobsSummaryPageTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make("core.Job", _quantity=1)
        self.client = Client()

    def test_if_returns_right_status_code(self):
        response = self.client.get("/summary/")
        self.assertEqual(response.status_code, 200)

    def test_if_job_data_is_in_page(self):
        response = self.client.get("/summary/")
        first_job = Job.objects.all().first()
        self.assertContains(response, first_job.title)
        self.assertContains(response, first_job.company_name)
        self.assertContains(response, first_job.workplace)


class PyJobsFeedTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make("core.Job", _quantity=1)
        self.client = Client()

    def test_if_feed_returns_right_status_code(self):
        response = self.client.get("/feed/")
        self.assertEqual(response.status_code, 200)

    def test_if_job_data_is_in_feed(self):
        response = self.client.get("/feed/")
        first_job = Job.objects.all().first()
        self.assertContains(response, first_job.title)
        self.assertContains(response, first_job.company_name)
        self.assertContains(response, first_job.workplace)


class PyJobsPremiumFeedTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make(
            "core.Job",
            _quantity=1,
            premium=True,
            premium_at=datetime.now(),
            title="Ola",
            company_name="test",
            workplace="test",
        )
        self.client = Client()

    def test_if_feed_returns_right_status_code(self):
        response = self.client.get("/feed/")
        self.assertEqual(response.status_code, 200)

    def test_if_job_data_is_in_feed(self):
        response = self.client.get("/feed/premium/")
        content = response.content.decode("utf-8")
        first_job = Job.objects.all().first()
        self.assertContains(response, first_job.title)
        self.assertContains(response, first_job.company_name)
        self.assertContains(response, first_job.workplace)


class PyJobsRobotsTXTTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_robots_txt_status_code(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)


class PyJobsJobCloseView(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
        )
        self.job.save()

    def _assert_close_link(self, kwargs, closed):
        url = reverse("close_job", kwargs=kwargs)
        response = self.client.get(url)
        if closed:
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, Job.objects.filter(is_open=True).count())
        else:
            self.assertEqual(302, response.status_code)
            self.assertEqual(1, Job.objects.filter(is_open=True).count())

    def test_valid_close_view(self):
        kwargs = {"pk": self.job.pk, "close_hash": self.job.close_hash()}
        self._assert_close_link(kwargs, closed=True)

    def test_close_view_for_non_existent_job(self):
        wrong_pk = self.job.pk + 1
        kwargs = {"pk": wrong_pk, "close_hash": self.job.close_hash()}
        self._assert_close_link(kwargs, closed=False)

    def test_close_view_with_wrong_hash(self):
        right_hash = self.job.close_hash()
        wrong_hash = right_hash[64:] + right_hash[:64]
        kwargs = {"pk": self.job.pk, "close_hash": wrong_hash}
        self._assert_close_link(kwargs, closed=False)


class PyJobsNormalViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_if_services_page_returns_200(self):
        response = self.client.get("/services/")
        self.assertEqual(response.status_code, 200)

    def test_if_job_creation_page_returns_200(self):
        response = self.client.get("/job/create/")
        self.assertEqual(response.status_code, 200)


class PyJobsRegisterNewJob(TestCase):
    def setUp(self):
        self.client = Client()

    @override_settings(RECAPTCHA_SECRET_KEY=None)
    def test_if_job_register_page_returns_200(self):
        response = self.client.post("/register/new/job/", follow=True)
        self.assertEqual(response.status_code, 200)

    @override_settings(RECAPTCHA_SECRET_KEY=None)
    def test_if_job_register_page_returns_error_if_form_is_filled_wrong(self):
        response = self.client.post("/register/new/job/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Falha na hora de criar o job" in content)

    @responses.activate
    @override_settings(RECAPTCHA_SECRET_KEY=None)
    def test_if_job_register_page_returns_error_if_form_is_filled_wrong(self):
        response = self.client.post("/register/new/job/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Falha na hora de criar o job" in content)

    @responses.activate
    @override_settings(RECAPTCHA_SECRET_KEY="AAA")
    @patch("pyjobs.core.views.JobForm")
    def test_if_job_register_page_returns_success_with_recaptcha(self, _mocked_form):
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": "Success"},
            status=200,
        )
        response = self.client.post("/register/new/job/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Acabamos de mandar um e-mail para vocês" in content)

    @override_settings(RECAPTCHA_SECRET_KEY="AAA")
    @responses.activate
    def test_if_job_register_page_returns_false_with_recaptcha(self):
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"failed": "yes"},
            status=200,
        )
        response = self.client.post("/register/new/job/", follow=True)
        content = response.content.decode("utf-8")
        self.assertTrue("Falha na hora de criar o job" in content)


class PyJobsJobChallenge(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
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

        self.client.login(username="jacob", password="top_secret")

    def test_if_job_that_is_not_challenging_redirects_to_job_page(self):
        response = self.client.get(
            "/job/{}/challenge_submit/".format(self.job.pk), follow=True
        )
        url = response.redirect_chain[0][0]
        self.assertEqual(url, "/job/{}/".format(self.job.pk))

    @patch("pyjobs.core.views.JobApplicationForm")
    def test_if_user_applies(self, _mocked_form):
        self.client.login(username="jacob", password="top_secret")
        self.job.is_challenging = True
        self.job.save()
        self.job.refresh_from_db()
        self.job_application = JobApplication.objects.create(
            job=self.job, user=self.user
        )
        self.job_application.refresh_from_db()
        mock_form = _mocked_form.return_value
        mock_form.is_valid.return_value = True

        response = self.client.post(
            "/job/{}/challenge_submit/".format(self.job.pk),
            data={"challenge_response_link": "http://www.google.com"},
            content_type="application/x-www-form-urlencoded",
            follow=True,
        )
        mock_form.save.assert_called()


class AppliedUsersDetailsTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )

        self.user = User.objects.create_user(
            username="jacob",
            first_name="jacob",
            last_name="bocaj",
            email="jacob@gmail.com",
            password="top_secret",
            is_staff=True,
        )

        self.profile = Profile.objects.create(
            user=self.user,
            github="http://www.github.com/foobar",
            linkedin="http://www.linkedin.com/in/foobar",
            portfolio="http://www.foobar.com/",
            cellphone="11981435390",
        )

        self.job_application = JobApplication.objects.create(
            user=self.user, job=self.job
        )

        self.client = Client()

        self.client.login(username="jacob", password="top_secret")

    def test_if_job_application_is_in_page(self):
        response = self.client.get("/job/{}/details/".format(self.job.pk))
        content = response.content.decode("utf-8")
        self.assertIn(self.user.first_name, content)
        self.assertIn(self.user.last_name, content)
        self.assertIn(self.profile.github, content)

    def test_if_get_job_applications_page_works(self):
        response = self.client.get("/job/{}/app/".format(self.job.pk))
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.first_name, body[1])
