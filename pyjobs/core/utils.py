from django.conf import settings
from telegram import Bot, TelegramError


def post_telegram_channel(message):
    if not settings.TELEGRAM_TOKEN and not settings.TELEGRAM_CHATID:
        return False, "missing_auth_keys"

    bot = Bot(settings.TELEGRAM_TOKEN)
    try:
        bot.send_message(chat_id=settings.TELEGRAM_CHATID, text=message)
    except TelegramError:
        return False, "wrong_auth_keys"

    return True, "success"
