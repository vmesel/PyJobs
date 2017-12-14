from django.conf.urls import url

from apps.jobs.views import *
from apps.core.views import interessados_no_job

urlpatterns = [
    url(r'^jobs/$', find_job, name='cadatre_job_freela'),
    url(r'^cadastro-job/$', create_job, name='cadatre_job_freela'),
    url(r'^job/(?P<pk>\d+)/', job_info, name='job_url'),
    url(r'^interessados/(?P<pk>\d+)/', interessados_no_job, name='interessados_csv'),
]
