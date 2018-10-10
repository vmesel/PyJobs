from django.conf.urls import url

from .views import *


urlpatterns = [

    url(r'^$', index, name="index"),
    url(r'^job/(?P<pk>\d+)/$', job_view, name='job_view'),
    url(r'^summary/$', summary_view, name='job_view'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^register/new/job/$', register_new_job, name='register_new_job'),
    url(r'^pythonistas/$', pythonistas_area, name='pythonistas_area'),
    url(r'^pythonistas/signup/$',
        pythonistas_signup, name='pythonistas_signup'),
    url(r'^password/$', pythonista_change_password, name='change_password'),
    url(r'^info/$', pythonista_change_info, name='change_info'),
]
