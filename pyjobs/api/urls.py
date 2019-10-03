from django.conf.urls import include, url

from pyjobs.api.views import JobResource, JobApplicationResource

app_name = "api"
urlpatterns = [
    url("^jobs/", include(JobResource.urls(name_prefix="job"))),
    url("^japps/", include(JobApplicationResource.urls(name_prefix="jobapplication"))),
]
