from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap

from .views import *

urlpatterns = [
    url(
        r"^partners/$",
        get_all_partners,
        name="get_all_partners",
    ),
]
