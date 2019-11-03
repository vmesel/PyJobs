from django.test import TestCase
from model_mommy import mommy
from unittest.mock import patch
from datetime import datetime
from django.contrib.auth.models import User
from pyjobs.core.models import Job
from pyjobs.core.admin import *


class TestUpdateCreatedAtFunc(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.jobs = mommy.make(Job, _quantity=10 * 3, public=True)

    def test_update_created_at(self):
        qs = Job.objects.all()
        created_at_value = self.jobs[0].created_at
        update_created_at("a", "request_here", self.jobs[:1])
        self.jobs[0].refresh_from_db()
        mod_created_at_value = self.jobs[0].created_at
        self.assertFalse(created_at_value == mod_created_at_value)

    @patch("pyjobs.core.admin.send_offer_email_template")
    def test_send_email_offer(self, _mocked_send_offer):
        send_email_offer("request", "request", self.jobs)
        _mocked_send_offer.assert_called()

    @patch("pyjobs.core.admin.send_feedback_collection_email")
    def test_send_feedback_collection_email(
        self, _mocked_send_feedback_collection_email
    ):
        send_feedback_collection("request", "request", self.jobs)
        _mocked_send_feedback_collection_email.assert_called()

    @patch("pyjobs.core.admin.subscribe_user_to_mailer")
    def test_subscribe_user_to_mailer(self, _mocked_subscribe_user_to_mailer):
        add_subscriber("request", "request", self.jobs)
        _mocked_subscribe_user_to_mailer.assert_called()


class TestSendingChallengesToOldApplicants(TestCase):
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
        self.job.save()

    @patch("pyjobs.core.admin.get_email_with_template")
    def test_sending(self, _mocked_get_email_with_template):
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

        self.job_application = JobApplication.objects.create(
            user=self.user, job=self.job
        )

        self.job.is_challenging = True
        self.job.save()

        self.jobs = [self.job]

        send_challenge_to_old_applicants("modeladmin", "request", self.jobs)
        _mocked_get_email_with_template.assert_called()
