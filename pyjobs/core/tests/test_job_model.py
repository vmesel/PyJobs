from datetime import datetime

from django.contrib.auth.models import User, AnonymousUser
from pyjobs.core.models import Job
from django.test import TestCase

class JobTest_01(TestCase):
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

    def test_job_created(self):
        self.assertTrue(Job.objects.exists())

    def test_job_created_at(self):
        self.assertIsInstance(self.job.created_at, datetime)

    def test_job_str(self):
        self.assertEqual(str(self.job), "Vaga 1")

    def test_job_application_link(self):
        self.assertEqual(str(self.job.get_application_link()), "http://www.xpto.com.br/apply")



class JobTest_02(TestCase):
    def setUp(self):
        self.job = Job(
            title="Vaga 2",
            workplace="Sao Paulo",
            company_name="XPTO",
            company_email = "vm@xpto.com",
            description="Job bem maneiro",
            public=True
        )
        self.job.save()

    def test_job_application_link(self):
        self.assertEqual(False, self.job.get_application_link())

    def test_publicly_available(self):
        self.assertTrue((self.job in Job.get_publicly_available_jobs()))

    def test_premium_available(self):
        self.assertTrue((self.job not in Job.get_premium_jobs()))


class JobTest_03(TestCase):
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

    def test_job_application_link(self):
        self.assertEqual(False, self.job.get_application_link())

    def test_premium_available(self):
        self.assertTrue((self.job in Job.get_premium_jobs()))

    def test_publicly_available(self):
        self.assertTrue((self.job not in Job.get_publicly_available_jobs()))

class JobTest_Application(TestCase):
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
        self.user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.job.save()

    def test_user_is_not_applied(self):
        application_status = self.job.applied(self.user)
        self.assertEqual(application_status, False)

    def test_user_is_not_applied(self):
        self.job.apply(self.user)
        application_status = self.job.applied(self.user)
        self.assertEqual(application_status, True)
