from django.conf import settings


def global_vars(request):
    return {"GA_CODE": settings.GA_CODE}
