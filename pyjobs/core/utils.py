from deouple import config
from facebook import GraphAPI

def list_fb_pages():
    graph = GraphAPI(config("FB_PYTHON_ACCESSTOKEN", default="TOKKEEEENNNN"))
    groups = graph.get_object("me/groups")
    return groups
