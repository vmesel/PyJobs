from decouple import config
from telegram import Bot, TelegramError

def post_telegram_channel(message):
    telegram_token = config('TELEGRAM_TOKEN', default=None)
    chat_id = config("TELEGRAM_CHATID", default=None)

    if None not in [telegram_token, chat_id]:
        bot = Bot(telegram_token)
        try:
            bot = Bot(telegram_token)
            bot.send_message(chat_id=chat_id, text=message)
            return True, 'success'

        except TelegramError:
            return False, 'wrong_auth_keys'

    return False, 'missing_auth_keys'
