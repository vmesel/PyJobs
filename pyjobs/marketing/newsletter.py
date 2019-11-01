from django.conf import settings
import requests
import json
from mailchimp3 import MailChimp


def subscribe_user_to_mailer(profile):
    status = True
    if not settings.MAILERLITE_API_KEY:
        return

    content = json.dumps({"email": profile.user.email})

    headers = {
        "content-type": "application/json",
        "x-mailerlite-apikey": settings.MAILERLITE_API_KEY,
    }

    try:
        req = requests.post("https://api.mailerlite.com/api/v2/subscribers", data=content, headers=headers)
    except:  # TODO specify which errors can be raised at this point
        status = False
    return status


def subscribe_user_to_chimp(profile):
    status = True
    configs = (
        settings.MAILCHIMP_API_KEY,
        settings.MAILCHIMP_USERNAME,
        settings.MAILCHIMP_LIST_KEY,
    )
    if not all(configs):
        return False

    client = MailChimp(settings.MAILCHIMP_API_KEY, settings.MAILCHIMP_USERNAME)
    try:
        client.lists.members.create(
            settings.MAILCHIMP_LIST_KEY,
            {"status": "subscribed", "email_address": profile.user.email},
        )
    except:  # TODO specify which errors can be raised at this point
        status = False
    return status
