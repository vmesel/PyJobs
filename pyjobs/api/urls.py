from django.conf.urls import url, include

from pyjobs.api.views import JobResource


app_name = 'api'
urlpatterns = [
    url('^jobs/', include(JobResource.urls(name_prefix='job'))),
]
