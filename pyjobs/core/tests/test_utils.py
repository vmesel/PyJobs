from django.test import TestCase
from unittest.mock import patch
from telegram import TelegramError

from pyjobs.core.utils import post_telegram_channel

class TelegramPosterTest(TestCase):

    def setUp(self):
        self.message = "Hello, World!"

    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    def test_post_message_to_telegram_successfully(self, mocked_bot, mocked_config):
        mocked_config.side_effect = ('my-token', 'my-channel')
        posted_message = post_telegram_channel(self.message)
        self.assertEqual(posted_message, (True, 'success'))

    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    def test_post_telegram_channel(self, mocked_bot, mocked_config):
        mocked_config.side_effect = ('my-token', 'my-channel')

        assert post_telegram_channel(self.message)[0]

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

        assert post_telegram_channel(self.message) == (False, 'missing_auth_keys')


    @patch('pyjobs.core.utils.config')
    @patch('pyjobs.core.utils.Bot')
    @patch('pyjobs.core.utils.post_telegram_channel')
    def test_post_wrong_auth_telegram_channel(self,
    mocked_post_telegram_channel, mocked_bot, mocked_config):

        mocked_post_telegram_channel.return_value = (False, 'wrong_auth_keys')
        mocked_config.side_effect = ('my-wrong-token', 'my-wrong-channel')

        assert mocked_post_telegram_channel(self.message) == (False, 'wrong_auth_keys')
