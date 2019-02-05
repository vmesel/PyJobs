from unittest.mock import patch

from django.test import TestCase
from telegram import TelegramError

from pyjobs.core.utils import post_telegram_channel


class TelegramPosterTest(TestCase):

    def setUp(self):
        self.message = "Hello, World!"

    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    def test_post_message_to_telegram_successfully(self, mocked_bot, mocked_config):
        mocked_config.side_effect = ('my-token', 'my-channel')
        result, message = post_telegram_channel(self.message)
        self.assertTrue(result)
        self.assertEqual(message, 'success')
        mocked_config.assert_any_call('TELEGRAM_TOKEN', default=None)
        mocked_config.assert_any_call('TELEGRAM_CHATID', default=None)
        mocked_bot.assert_called_with('my-token')
        mocked_bot.return_value.send_message.assert_called_with(
            chat_id='my-channel',
            text=self.message
        )

    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    def test_post_no_auth_telegram_channel(self, mocked_bot, mocked_config):
        mocked_config.side_effect = (None, None)
        result, message = post_telegram_channel(self.message)
        self.assertFalse(result)
        self.assertEqual(message, 'missing_auth_keys')

    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    def test_post_wrong_auth_telegram_channel(self, mocked_bot, mocked_config):
        mocked_config.side_effect = ('my-token', 'my-channel')
        mocked_bot.return_value.send_message.side_effect = TelegramError('error')
        result, message = post_telegram_channel(self.message)
        self.assertFalse(result)
        self.assertEqual(message, 'wrong_auth_keys')
        mocked_config.assert_any_call('TELEGRAM_TOKEN', default=None)
        mocked_config.assert_any_call('TELEGRAM_CHATID', default=None)
        mocked_bot.assert_called_once_with('my-token')
        mocked_bot.return_value.send_message.assert_called_with(
            chat_id='my-channel',
            text=self.message
        )