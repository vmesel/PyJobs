from django.conf import settings
from social_django.models import UserSocialAuth


def append_social_info_to_context(request):
    return_content = {}

    try:
        user = request.user
    except:
        user = None

    try:
        return_content["GITHUB_LOGIN"] = user.social_auth.get(provider="github")
    except (UserSocialAuth.DoesNotExist, AttributeError):
        return_content["GITHUB_LOGIN"] = False

    try:
        return_content["LINKEDIN_LOGIN"] = user.social_auth.get(
            provider="linkedin-oauth2"
        )
    except (UserSocialAuth.DoesNotExist, AttributeError):
        return_content["LINKEDIN_LOGIN"] = False

    return_content["SOCIAL_AUTH"] = (
        return_content["GITHUB_LOGIN"] or return_content["LINKEDIN_LOGIN"]
    )
    return_content["EMPTY_PROFILE"] = return_content["SOCIAL_AUTH"] and not (
        request.user.profile.linkedin
        or request.user.profile.github
        or request.user.profile.portfolio
        or request.user.profile.cellphone
    )

    return return_content


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
        **append_social_info_to_context(request),
    }
