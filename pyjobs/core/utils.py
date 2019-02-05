from decouple import config
import telegram


def post_telegram_channel(message):
    telegram_token = config('TELEGRAM_TOKEN', default=None)
    if telegram_token != None:
        bot = telegram.Bot(telegram_token)
        try:
            bot.send_message(chat_id = config("TELEGRAM_CHATID"), text=message)
        except:
            pass
    return True
