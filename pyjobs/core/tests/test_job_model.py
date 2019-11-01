from datetime import datetime, timedelta
from hashlib import sha512
from unittest.mock import patch
import responses
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import Recipe

from pyjobs.core.models import Job, Profile, Skill, JobError


class JobTest_01(TestCase):
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
        self.email, *_ = mail.outbox

    def test_job_created(self):
        self.assertTrue(Job.objects.exists())

    def test_job_created_at(self):
        self.assertIsInstance(self.job.created_at, datetime)

    def test_job_str(self):
        self.assertEqual(str(self.job), "Vaga 1")

    def test_job_application_link(self):
        self.assertEqual(
            str(self.job.get_application_link()), "http://www.xpto.com.br/apply"
        )

    def test_job_url_is_sent_in_the_email(self):
        self.assertIn("/job/{}/".format(self.job.pk), self.email.body)

    def test_close_hash(self):
        value = "::".join(
            ("close", "Foo Bar", str(self.job.pk), str(self.job.created_at))
        )
        hash_obj = sha512(value.encode("utf-8"))
        self.assertEqual(self.job.close_hash("Foo Bar"), hash_obj.hexdigest())

    def test_close_url(self):
        self.assertEqual(
            f"/job/close/{self.job.pk}/{self.job.close_hash()}/",
            self.job.get_close_url(),
        )

    def test_close_url_is_sent_in_the_email(self):
        self.assertIn(self.job.get_close_url(), self.email.body)


class JobTest_02(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 2",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            public=True,
        )
        self.job.save()

    def test_job_application_link(self):
        self.assertEqual(False, self.job.get_application_link())

    def test_publicly_available(self):
        self.assertTrue((self.job in Job.get_publicly_available_jobs()))

    def test_premium_available(self):
        self.assertTrue((self.job not in Job.get_premium_jobs()))


class JobTest_03(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )
        self.job.save()
        self.job.premium_at = self.job.created_at
        self.job.save()

    def test_job_application_link(self):
        self.assertEqual(False, self.job.get_application_link())

    def test_premium_available(self):
        self.assertTrue((self.job in Job.get_premium_jobs()))

    def test_publicly_available(self):
        self.assertTrue((self.job not in Job.get_publicly_available_jobs()))


class JobTest_Application(TestCase):
    @responses.activate
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )

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

        self.job.save()

    def test_user_is_not_applied(self):
        application_status = self.job.applied(self.user)
        self.assertEqual(application_status, False)

    def test_user_is_applied(self):
        self.job.apply(self.user)
        application_status = self.job.applied(self.user)
        self.assertEqual(application_status, True)


class JobTest_04(TestCase):
    @responses.activate
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

        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        mommy.make("core.Skill", _quantity=7, _fill_optional=True)

        self.job.skills = Skill.objects.all()[:5]
        self.job.save()

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

    def test_user_has_no_skills(self):
        self.assertFalse(self.profile.profile_skill_grade(self.job.pk))

    @responses.activate
    def test_user_0_graded(self):
        self.profile.skills = Skill.objects.all()[5:]
        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )
        self.profile.save()
        self.assertEqual(self.profile.profile_skill_grade(self.job.pk), 0.0)

    @responses.activate
    def test_user_100_graded(self):
        self.profile.skills = Skill.objects.all()
        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )
        self.profile.save()
        self.assertEqual(self.profile.profile_skill_grade(self.job.pk), 100.0)


class JobTest_05(TestCase):
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

        mommy.make("core.Skill", _quantity=1, _fill_optional=True)

        self.job.skills = Skill.objects.all()
        self.job.save()

        self.job.created_at += -timedelta(14)
        self.job.save()

    def test_if_job_is_listed_in_get_jobs_to_get_feedback(self):
        jobs_to_feedback = self.job.get_jobs_to_get_feedback()
        self.assertTrue(self.job in jobs_to_feedback)


class JobTest_06(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 3",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
            public=True,
        )

    def test_if_job_is_not_created_and_close_hash_is_unavailable(self):
        jobs = Job.objects.all()
        self.assertFalse(self.job in jobs)

        self.assertRaisesMessage(
            JobError, "Unsaved Job models have no close hash", self.job.close_hash
        )

    def test_if_job_is_not_created_and_close_url_is_unavailable(self):
        jobs = Job.objects.all()
        self.assertFalse(self.job in jobs)

        self.assertRaisesMessage(
            JobError, "Unsaved Job models have no close URL", self.job.get_close_url
        )


class JobSkillsTest(TestCase):
    def setUp(self):
        self.skill = Recipe(Skill).make()

    def test_if_str_rep_is_ok(self):
        self.assertEqual(self.skill.__str__(), self.skill.name)

    def test_if_repr_rep_is_ok(self):
        self.assertEqual(self.skill.__repr__(), self.skill.name)


class JobManagerTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Job(
            title="Vaga 1",
            workplace="Sao Paulo",
            company_name="XPTO",
            application_link="http://www.xpto.com.br/apply",
            company_email="vm@xpto.com",
            description="Job bem maneiro",
            premium=True,
        )
        self.job.created_at = datetime.now() - timedelta(14)
        self.job.premium_at = datetime.now() - timedelta(14)
        self.job.save()

    def test_if_job_in_premium_manager(self):
        qs = Job.objects.premium().created_in_the_last(30, premium=True)
        qs_term = Job.objects.search(term="Vaga 1")

        self.assertIn(self.job, qs)
        self.assertIn(self.job, qs_term)
