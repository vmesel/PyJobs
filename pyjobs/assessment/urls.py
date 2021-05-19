from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse

from pyjobs.assessment.views import *

urlpatterns = [
    url(r"^(?P<unique_slug>[-\w\d]+)/$", quiz_home, name="quiz_home"),
    url(r"^(?P<unique_slug>[-\w\d]+)/question/$", question_page, name="question_page"),
    url(
        r"^(?P<unique_slug>[-\w\d]+)/answer/(?P<question_id>[\d]+)/$",
        question_submit,
        name="question_submit",
    ),
    url(
        r"^(?P<unique_slug>[-\w\d]+)/thumb/$",
        quiz_thumbnail,
        name="quiz_thumbnail",
    ),
]
