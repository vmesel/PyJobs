from datetime import datetime, timedelta
from hashlib import sha512
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from model_mommy import mommy

from pyjobs.core.models import Job, Profile, Skill


class JobTest_01(TestCase):
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
    @patch("pyjobs.core.models.post_telegram_channel")
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
    @patch("pyjobs.core.models.post_telegram_channel")
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

    def test_job_application_link(self):
        self.assertEqual(False, self.job.get_application_link())

    def test_premium_available(self):
        self.assertTrue((self.job in Job.get_premium_jobs()))

    def test_publicly_available(self):
        self.assertTrue((self.job not in Job.get_publicly_available_jobs()))


class JobTest_Application(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
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

    def test_user_0_graded(self):
        self.profile.skills = Skill.objects.all()[5:]
        self.profile.save()
        self.assertEqual(self.profile.profile_skill_grade(self.job.pk), 0.0)

    def test_user_100_graded(self):
        self.profile.skills = Skill.objects.all()
        self.profile.save()
        self.assertEqual(self.profile.profile_skill_grade(self.job.pk), 100.0)


class JobTest_05(TestCase):
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

        mommy.make("core.Skill", _quantity=1, _fill_optional=True)

        self.job.skills = Skill.objects.all()
        self.job.save()

        self.job.created_at += -timedelta(14)
        self.job.save()

    def test_if_job_is_listed_in_get_jobs_to_get_feedback(self):
        jobs_to_feedback = self.job.get_jobs_to_get_feedback()
        self.assertTrue(self.job in jobs_to_feedback)
