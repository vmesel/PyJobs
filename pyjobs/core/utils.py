from decouple import config
from telegram import Bot


def post_telegram_channel(message):
    telegram_token = config('TELEGRAM_TOKEN', default=None)
    if telegram_token != None:
        bot = Bot(telegram_token)
        try:
            bot.send_message(chat_id = config("TELEGRAM_CHATID"), text=message)
        except:
            pass
    return True
