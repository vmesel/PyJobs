from decouple import config
from facebook import GraphAPI
import telegram

def list_fb_pages():
    graph = GraphAPI(config("FB_PYTHON_ACCESSTOKEN", default="TOKKEEEENNNN"))
    groups = graph.get_object("me/groups")
    return groups

def post_fb_page(message):
    graph = GraphAPI(config("FB_PYTHON_ACCESSTOKEN", default="TOKKEEEENNNN"))
    try:
        graph.put_object("PyJobs", "feed", message=message)
    except:
        pass
    return True

def post_telegram_channel(message):
    bot = telegram.Bot(config('TELEGRAM_TOKEN'))
    try:
        bot.send_message(chat_id = config("TELEGRAM_CHATID"), text=message)
    except:
        pass
    return True
