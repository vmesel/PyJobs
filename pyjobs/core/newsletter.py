from django.conf import settings
from mailchimp3 import MailChimp


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
