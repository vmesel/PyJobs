from decouple import config
<<<<<<< HEAD
from telegram import Bot, TelegramError
=======
from telegram import Bot
>>>>>>> b0ce866601a5ff5cd317609bd0bb088877b32e35


def post_telegram_channel(message):
    telegram_token = config('TELEGRAM_TOKEN', default=None)
<<<<<<< HEAD
    chat_id = config("TELEGRAM_CHATID", default=None)

    if None not in [telegram_token, chat_id]:
=======
    if telegram_token != None:
        bot = Bot(telegram_token)
>>>>>>> b0ce866601a5ff5cd317609bd0bb088877b32e35
        try:
            bot = Bot(telegram_token)
            bot.send_message(chat_id=chat_id, text=message)
            return True, 'success'

        except TelegramError:
            return False, 'wrong_auth_keys'

    return False, 'missing_auth_keys'
