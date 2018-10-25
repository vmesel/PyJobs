from django.conf.urls import url
from core.decorators import check_recaptcha
from core.views import *


urlpatterns = [
    url(r'^$', Index.as_view(), name="index"),
    url(r'^job/(?P<pk>\d+)/$', job_view, name='job_view'),
    url(r'^summary/$', SummaryListView.as_view(), name='job_view'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^register/new/job/$', check_recaptcha(RegisterJob.as_view()), name='register_job'),
    url(r'^pythonistas/$', Pythonistas.as_view(), name='pythonistas_area'),
    url(r'^pythonistas/signup/$',
        pythonistas_signup, name='pythonistas_signup'),
    url(r'^password/$', pythonista_change_password, name='change_password'),
    url(r'^info/$', pythonista_change_info, name='change_info'),
    url(r'^robots.txt$', RobotsView.as_view(), name='robots'),

]
