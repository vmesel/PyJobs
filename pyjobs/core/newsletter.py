from django.conf import settings
import requests
from mailchimp3 import MailChimp


def subscribe_user_to_mailer(profile):
    if not settings.MAILERLITE_API_KEY:
        return

    content = {"email": profile.user.email}

    headers = {
        "content-type": "application/json",
        "x-mailerlite-apikey": settings.MAILERLITE_API_KEY,
    }

    url = "https://api.mailerlite.com/api/v2/subscribers"

    try:
        req = requests.post(url, data=content, headers=headers)
    except:  # TODO specify which errors can be raised at this point
        pass


def subscribe_user_to_chimp(profile):
    configs = (
        settings.MAILCHIMP_API_KEY,
        settings.MAILCHIMP_USERNAME,
        settings.MAILCHIMP_LIST_KEY,
    )
    if not all(configs):
        return

    client = MailChimp(settings.MAILCHIMP_API_KEY, settings.MAILCHIMP_USERNAME)
    try:
        client.lists.members.create(
            settings.MAILCHIMP_LIST_KEY,
            {"status": "subscribed", "email_address": profile.user.email},
        )
    except:  # TODO specify which errors can be raised at this point
        pass
