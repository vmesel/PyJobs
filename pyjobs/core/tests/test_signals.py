from datetime import datetime, timedelta
from hashlib import sha512
from unittest.mock import patch
import responses
from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import Recipe

from pyjobs.core.models import (
    Job,
    Profile,
    JobApplication,
    Contact,
    send_feedback_collection_email,
    Messages,
    send_offer_email_template,
)
from django.db.models.signals import post_save


class JobApplicationSignalTest(TestCase):
    @responses.activate
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Recipe(Job, premium=True, public=True, is_challenging=True).make()

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

    def test_job_application_triggered_email(self):
        with patch("pyjobs.core.models.send_email_notifing_job_application") as mocked:
            post_save.connect(mocked, sender=JobApplication)

        self.job_application = JobApplication(user=self.user, job=self.job)

        self.job_application.save()

        self.assertTrue(mocked.called)
        self.assertEqual(
            "{} applied to {}".format(self.user, self.job),
            self.job_application.__str__(),
        )


class ContactSignalTest(TestCase):
    def test_contact_signal_is_called(self):
        with patch("pyjobs.core.models.new_contact") as mocked_contact:
            post_save.connect(mocked_contact, sender=Contact)

        self.contact = Recipe(Contact).make()

        self.assertTrue(mocked_contact.called)


class HelpersSignalsTest(TestCase):
    @patch("pyjobs.core.models.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Recipe(Job, premium=True, public=True, is_challenging=True).make()

    @patch("pyjobs.core.models.send_mail")
    def test_helper_send_feedback_collection_email(self, mocked_send_mail):
        self.feedback_email = Recipe(Messages, message_type="feedback").make()

        send_feedback_collection_email(self.job)

        self.assertTrue(mocked_send_mail.called)

    @patch("pyjobs.core.models.send_mail")
    def test_helper_send_offer_email_template(self, mocked_send_mail):
        self.offer_email = Recipe(Messages, message_type="offer").make()

        send_offer_email_template(self.job)

        self.assertTrue(mocked_send_mail.called)
