from decouple import config
from facebook import GraphAPI
import telegram

def list_fb_pages():
    token = config("FB_PYTHON_ACCESSTOKEN", default=None)
    if token != None:
        graph = GraphAPI(token)
        groups = graph.get_object("me/groups")
        return groups
    return []

def post_fb_page(message):
    token = config("FB_PYTHON_ACCESSTOKEN", default=None)
    if token != None:
        graph = GraphAPI(token)
        try:
            graph.put_object("PyJobs", "feed", message=message)
        except:
            pass
        return True
    return False

def post_telegram_channel(message):
    telegram_token = config('TELEGRAM_TOKEN', default=None)
    if telegram_token != None:
        bot = telegram.Bot(telegram_token)
        try:
            bot.send_message(chat_id = config("TELEGRAM_CHATID"), text=message)
        except:
            pass
    return True
