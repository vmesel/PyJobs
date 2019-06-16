from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import resolve, reverse
from model_mommy import mommy

from pyjobs.core.models import Job, Profile
from pyjobs.core.views import index


class HomeJobsViewsTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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
        self.home_page = resolve("/")
        self.request = HttpRequest()
        self.home_page_html = index(self.request).content.decode("utf-8")

    def test_job_is_in_websites_home(self):
        self.assertEqual(self.home_page.func, index)

    def test_job_in_home(self):
        job_title = str(self.job)
        self.assertTrue(job_title in self.home_page_html)

    def test_job_url_is_in_home(self):
        job_url = "/job/{}/".format(str(self.job.pk))
        self.assertTrue(job_url in self.home_page_html)


class JobDetailsViewTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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

    def test_job_application_link_in_view(self):
        self.assertTrue(self.job.application_link in self.job_view_html)

    def test_job_description_in_view(self):
        self.assertTrue(self.job.description in self.job_view_html)

    def test_job_requirements_in_view(self):
        self.assertTrue(self.job.requirements in self.job_view_html)


class PyJobsJobApplication(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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

    def test_check_applied_for_job_anon(self):
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode("utf-8")
        expected_response = (
            "Você precisa estar logado para se candidatar para esta vaga!"
        )
        self.assertTrue(expected_response in request)

    def test_check_applied_for_job(self):
        self.client.login(username="jacob", password="top_secret")
        request_client = self.client.get("/job/{}/".format(self.job.pk))
        request = request_client.content.decode("utf-8")
        expected_response = "Candidate-se para esta vaga pelo PyJobs"
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


class PyJobsMultipleJobsPagesTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make("core.Job", _quantity=14)
        self.client = Client()

    def test_first_page(self):
        response = self.client.get("/?page=1")
        self.assertTrue(response.status_code == 200)

    def test_second_page(self):
        response = self.client.get("/?page=2")
        self.assertTrue(response.status_code == 200)

    def test_third_page_redirection(self):
        response = self.client.get("/?page=3")
        self.assertRedirects(response, "/", status_code=302, target_status_code=200)

    def test_string_in_page_redirection(self):
        response = self.client.get("/?page=ola")
        self.assertRedirects(response, "/", status_code=302, target_status_code=200)


class PyJobsSummaryPageTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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
    @patch("pyjobs.core.models.post_telegram_channel")
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
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        mommy.make("core.Job", _quantity=1, premium=True)
        self.client = Client()

    def test_if_premium_feed_returns_right_status_code(self):
        response = self.client.get("/feed/premium/")
        self.assertEqual(response.status_code, 200)

    def test_if_premium_job_data_is_in_feed(self):
        response = self.client.get("/feed/premium/")
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


class PyJobsJobDeleteView(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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

    def _assert_delete_link(self, kwargs, deleted):
        url = reverse("delete_job", kwargs=kwargs)
        response = self.client.get(url)
        if deleted:
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, Job.objects.count())
        else:
            self.assertEqual(404, response.status_code)
            self.assertEqual(1, Job.objects.count())

    def test_valid_delete_view(self):
        kwargs = {"pk": self.job.pk, "delete_hash": self.job.delete_hash()}
        self._assert_delete_link(kwargs, deleted=True)

    def test_delete_view_for_non_existent_job(self):
        wrong_pk = self.job.pk + 1
        kwargs = {"pk": wrong_pk, "delete_hash": self.job.delete_hash()}
        self._assert_delete_link(kwargs, deleted=False)

    def test_delete_view_with_wrong_hash(self):
        right_hash = self.job.delete_hash()
        wrong_hash = right_hash[64:] + right_hash[:64]
        kwargs = {"pk": self.job.pk, "delete_hash": wrong_hash}
        self._assert_delete_link(kwargs, deleted=False)
