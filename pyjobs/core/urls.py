from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse

from pyjobs.core.models import Job, Skill
from pyjobs.core.views import *


class BlogBasedSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        posts = []
        post_request = requests.get(f"{settings.BLOG_API_URL}posts/").json()
        for post in post_request["posts"]:
            posts.append(post["slug"])

        return posts

    def location(self, item):
        return reverse("blog_post", args=[item])


class PyJobsLocationBasedSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return [
            "acre",
            "alagoas",
            "amapa",
            "amazonas",
            "bahia",
            "ceara",
            "distrito-federal",
            "espirito-santo",
            "goias",
            "maranhao",
            "mato-grosso",
            "mato-grosso-do-sul",
            "minas-gerais",
            "para",
            "paraiba",
            "parana",
            "pernambuco",
            "piaui",
            "rio-de-janeiro",
            "rio-grande-do-norte",
            "rio-grande-do-sul",
            "rondonia",
            "roraima",
            "santa-catarina",
            "sao-paulo",
            "sergipe",
            "tocantins",
        ]

    def location(self, item):
        return reverse("job_state_view", args=[item])


class PyJobsSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["index", "privacy", "services", "job_creation", "blog_index"]

    def location(self, item):
        return reverse(item)


class PyJobsJobsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Job.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class PyJobsSkillsSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return [skill.unique_slug for skill in Skill.objects.all()]

    def location(self, item):
        return reverse("job_skill_view", args=[item])


urlpatterns = [
    url(r"^$", index, name="index"),
    url(r"^jobs/$", jobs, name="jobs"),
    url(r"^privacy/$", privacy, name="privacy"),
    url(r"^summary/$", summary_view, name="job_view"),
    url(r"^services/$", services_view, name="services"),
    url(r"^contact/$", contact, name="contact"),
    url(r"^register/new/job/$", register_new_job, name="register_new_job"),
    url(r"^user/$", pythonistas_area, name="pythonistas_area"),
    url(r"^user/signup/$", pythonistas_signup, name="pythonistas_signup"),
    url(r"^user/password/$", pythonista_change_password, name="change_password"),
    url(r"^user/info/$", pythonista_change_info, name="change_info"),
    url(r"^user/applied-to/$", pythonista_applied_info, name="applied_to_info"),
    url(r"^user/proficiency/$", pythonistas_proficiency, name="user_proficiency"),
    url(r"^job/create/$", job_creation, name="job_creation"),
    url(r"^jobs/location/(?P<state>[-\w\d]+)/$", job_state_view, name="job_state_view"),
    url(
        r"^jobs/skill/(?P<unique_slug>[-\w\d]+)/$",
        job_skill_view,
        name="job_skill_view",
    ),
    url(r"^thumb/(?P<unique_slug>[-\w\d]+)/$", thumbnail_view, name="thumbnail_view"),
    url(
        r"^job/(?P<unique_slug>[-\w\d]+)/details/$",
        applied_users_details,
        name="applied_users_details",
    ),
    url(
        r"^job/(?P<unique_slug>[-\w\d]+)/app/$",
        get_job_applications,
        name="get_job_applications",
    ),
    url(
        r"^job/(?P<unique_slug>[-\w\d]+)/challenge_submit/$",
        job_application_challenge_submission,
        name="job_application_challenge_submission",
    ),
    url(r"^job/(?P<unique_slug>[-\w\d]+)/$", job_view, name="job_view"),
    url(
        r"^job/close/(?P<unique_slug>[-\w\d]+)/(?P<close_hash>[\da-f]{128})/$",
        close_job,
        name="close_job",
    ),
    url(r"^lp/landing01/$", fb_ads_landing, name="fb_ads_landing"),
    url(
        r"^job/application/(?P<pk>[\d]+)/$",
        job_application_feedback,
        name="job_application_feedback",
    ),
    url(r"^robots.txt$", robots_view, name="robots"),
    url(
        r"^sitemap\.xml$",
        sitemap,
        {
            "sitemaps": {
                "jobs": PyJobsJobsSitemap(),
                "site": PyJobsSitemap(),
                "location": PyJobsLocationBasedSitemap(),
                "skills": PyJobsSkillsSitemap(),
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
    url(r"^select2/", include("django_select2.urls")),
    url(r"^feed/$", JobsFeed()),
    url(r"^feed/premium/$", PremiumJobsFeed()),
]
