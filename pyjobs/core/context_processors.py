from django.conf import settings


def global_vars(request):
    return {
        "GA_CODE": settings.GA_CODE,
        "WEBSITE_NAME": settings.WEBSITE_NAME,
        "WEBSITE_URL": settings.WEBSITE_URL,
        "WEBSITE_SLOGAN": settings.WEBSITE_SLOGAN,
        "WEBSITE_OWNER_EMAIL": settings.WEBSITE_OWNER_EMAIL,
        "WEBSITE_GENERAL_EMAIL": settings.WEBSITE_GENERAL_EMAIL,
        "WEBSITE_WORKING_LANGUAGE": settings.WEBSITE_WORKING_LANGUAGE,
        "WEBSITE_MAILINGLIST_LINK": settings.WEBSITE_MAILINGLIST_LINK,
        "USER_SUBSTANTIVE": settings.USER_SUBSTANTIVE,
        "VAPID_PUBLIC_KEY": settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"],
    }
