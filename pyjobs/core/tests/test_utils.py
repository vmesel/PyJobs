from django.test import TestCase
from unittest.mock import patch

from pyjobs.core.utils import post_telegram_channel

class TelegramPosterTest(TestCase):

    @patch('telegram.Bot')
    def setUp(self, _mocked_telegram_bot):
        self.message = "Hello, World!"

    def test_post_message_to_telegram(self):
        posted_message = post_telegram_channel(self.message)
        self.assertEqual(posted_message, True)
