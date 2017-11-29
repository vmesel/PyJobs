from django.conf.urls import url

from apps.jobs.views import *

urlpatterns = [
    url(r'^jobs/$', find_job, name='cadatre_job_freela'),
    url(r'^cadastro-job/$', create_job, name='cadatre_job_freela'),
    url(r'^job/(?P<pk>\d+)/', job_info, name='job_url'),
]
