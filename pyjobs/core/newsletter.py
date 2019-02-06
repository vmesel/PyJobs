from django.conf import settings
from mailchimp3 import MailChimp


def subscribe_user_to_chimp(profile):
    api_key = settings.MAILCHIMP_API_KEY
    user_api = settings.MAILCHIMP_USERNAME
    list_id = settings.MAILCHIMP_LIST_KEY

    if not all([api_key, user_api, list_id]):
        return False

    try:
        client = MailChimp(api_key, user_api)
        client.lists.members.create(list_id, {
            'status': 'subscribed',
            'email_address': profile.user.email,
        })
        return True

    except:
        return False
