from mailchimp3 import MailChimp
from decouple import config

def subscribe_user_to_chimp(profile):
    api_key = config("MAILCHIMP_API_KEY", default=None)
    user_api = config("MAILCHIMP_USERNAME", default=None)
    list_id = config("MAILCHIMP_LIST_KEY", default=None)
    if api_key != None:
        client = MailChimp(api_key, user_api)
        try:
            client.lists.members.create(list_id, {
                'status': 'subscribed',
                'email_address': profile.user.email,
            })
        except:
            pass
    return False
