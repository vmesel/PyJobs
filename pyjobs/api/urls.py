from django.conf.urls import include, url

from pyjobs.api.views import JobResource

app_name = 'api'
urlpatterns = [
    url('^jobs/', include(JobResource.urls(name_prefix='job'))),
]
