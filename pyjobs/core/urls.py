from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap

from pyjobs.core.models import Job
from pyjobs.core.views import *


class PyJobsSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def items(self):
        return Job.get_publicly_available_jobs()

    def lastmod(self, obj):
        return obj.created_at


urlpatterns = [
    url(r"^$", index, name="index"),
    url(r"^jobs/$", jobs, name="jobs"),
    url(r"^job/(?P<pk>\d+)/$", job_view, name="job_view"),
    url(
        r"^job/close/(?P<pk>\d+)/(?P<close_hash>[\da-f]{128})/$",
        close_job,
        name="close_job",
    ),
    url(r"^summary/$", summary_view, name="job_view"),
    url(r"^services/$", services_view, name="services"),
    url(r"^contact/$", contact, name="contact"),
    url(r"^register/new/job/$", register_new_job, name="register_new_job"),
    url(r"^pythonistas/$", pythonistas_area, name="pythonistas_area"),
    url(r"^pythonistas/signup/$", pythonistas_signup, name="pythonistas_signup"),
    url(r"^password/$", pythonista_change_password, name="change_password"),
    url(r"^info/$", pythonista_change_info, name="change_info"),
    url(r"^applied-to/$", pythonista_applied_info, name="applied_to_info"),
    url(r"^thumb/(?P<pk>\d+)/$", thumbnail_view, name="thumbnail_view"),
    url(
        r"^job/(?P<pk>\d+)/details/$",
        applied_users_details,
        name="applied_users_details",
    ),
    url(r"^job/(?P<pk>\d+)/app/$", get_job_applications, name="get_job_applications"),
    url(
        r"^job/(?P<pk>\d+)/challenge_submit/$",
        job_application_challenge_submission,
        name="job_application_challenge_submission",
    ),
    url(r"^job/create/$", job_creation, name="job_creation"),
    url(r"^lp/landing01/$", fb_ads_landing, name="fb_ads_landing"),
    url(r"^robots.txt$", robots_view, name="robots"),
    url(
        r"^sitemap\.xml$",
        sitemap,
        {"sitemaps": {"jobs": PyJobsSitemap()}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    url(r"^select2/", include("django_select2.urls")),
    url(r"^feed/$", JobsFeed()),
    url(r"^feed/premium/$", PremiumJobsFeed()),
]
