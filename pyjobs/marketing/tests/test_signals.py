from datetime import datetime
from unittest.mock import patch
from django.test import TestCase
from model_mommy.recipe import Recipe

from pyjobs.marketing.triggers import send_feedback_collection_email, send_offer_email_template
from pyjobs.marketing.models import Contact, Messages
from django.db.models.signals import post_save

from pyjobs.core.models import Job

class ContactSignalTest(TestCase):
    def test_contact_signal_is_called(self):
        with patch("pyjobs.marketing.models.new_contact") as mocked_contact:
            post_save.connect(mocked_contact, sender=Contact)

        self.contact = Recipe(Contact).make()

        self.assertTrue(mocked_contact.called)


class HelpersSignalsTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.job = Recipe(Job, premium=True, public=True, is_challenging=True).make()

    @patch("pyjobs.marketing.triggers.send_mail")
    def test_helper_send_feedback_collection_email(self, mocked_send_mail):
        from pyjobs.marketing.models import Contact, Messages
        self.feedback_email = Recipe(Messages, message_type="feedback").make()

        send_feedback_collection_email(self.job)

        self.assertTrue(mocked_send_mail.called)

    @patch("pyjobs.marketing.triggers.send_mail")
    def test_helper_send_offer_email_template(self, mocked_send_mail):
        from pyjobs.marketing.models import Contact, Messages
        self.offer_email = Recipe(Messages, message_type="offer").make()

        send_offer_email_template(self.job)

        self.assertTrue(mocked_send_mail.called)
