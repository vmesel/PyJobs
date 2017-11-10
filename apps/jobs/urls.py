from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^jobs/$', views.JobListView.as_view(), name='cadatre_job_freela'),
    url(r'^cadastro-job/$', views.create_job, name='cadatre_job_freela'),
    url(r'^job/(?P<pk>\d+)/', views.job_info, name='job_url'),
]
