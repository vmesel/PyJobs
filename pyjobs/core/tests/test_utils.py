from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.mail import EmailMultiAlternatives
from telegram import TelegramError

from pyjobs.core.utils import *
from pyjobs.core.email_utils import *
from pyjobs.core.models import Job


class TelegramPosterTest(TestCase):
    def setUp(self):
        self.message = "Hello, World!"

    @override_settings(TELEGRAM_TOKEN="my-token")
    @override_settings(TELEGRAM_CHATID="my-channel")
    @patch("pyjobs.core.utils.Bot")
    def test_post_message_to_telegram_successfully(self, mocked_bot):
        result, message = post_telegram_channel(self.message)
        self.assertTrue(result)
        self.assertEqual(message, "success")
        mocked_bot.assert_called_with("my-token")
        mocked_bot.return_value.send_message.assert_called_with(
            chat_id="my-channel", text=self.message
        )

    @override_settings(TELEGRAM_TOKEN=None)
    @override_settings(TELEGRAM_CHATID=None)
    @patch("pyjobs.core.utils.Bot")
    def test_post_no_auth_telegram_channel(self, mocked_bot):
        result, message = post_telegram_channel(self.message)
        self.assertFalse(result)
        self.assertEqual(message, "missing_auth_keys")

    @override_settings(TELEGRAM_TOKEN="my-token")
    @override_settings(TELEGRAM_CHATID="my-channel")
    @patch("pyjobs.core.utils.Bot")
    def test_post_wrong_auth_telegram_channel(self, mocked_bot):
        mocked_bot.return_value.send_message.side_effect = TelegramError("error")
        result, message = post_telegram_channel(self.message)
        self.assertFalse(result)
        self.assertEqual(message, "wrong_auth_keys")
        mocked_bot.assert_called_once_with("my-token")
        mocked_bot.return_value.send_message.assert_called_with(
            chat_id="my-channel", text=self.message
        )


class HTMLEmailSenderTest(TestCase):
    # TODO: Implement more tests on this function so it can be reliable
    def setUp(self):
        self.to_emails = ["localhost@localhost"]
        self.subject = "Hey guys, just testing around here!"
        self.template_name = "published_job"

    def test_returned_object_has_defined_attributes(self):
        msg = get_email_with_template(
            self.template_name, {}, self.subject, self.to_emails
        )

        self.assertTrue(msg.subject == self.subject)
        self.assertTrue(msg.to == self.to_emails)
