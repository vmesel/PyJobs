from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap

from pyjobs.marketing.views import *

urlpatterns = [
    url(r"^job/(?P<pk>\d+)/share/$", sharing_job_view, name="sharing_job_view",),
]
