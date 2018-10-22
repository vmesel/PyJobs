"""pyjobs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from .settings import *
from core.views import *
from api.resources import *
from django.contrib.auth import views as auth_views

job_resource = JobResource()

urlpatterns = [
    url(r'^admin_v2/', admin.site.urls),
    url(r'^api/', include(job_resource.urls)),
    url(r'^$', index, name="index"),
    url(r'^job/(?P<pk>\d+)/$', job_view, name='job_view'),
    url(r'^summary/$', SummaryListView.as_view(), name='job_view'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^register/new/job/$', register_new_job, name='register_new_job'),
    url(r'^pythonistas/$', Pythonistas.as_view(), name='pythonistas_area'),
    url(r'^pythonistas/signup/$', pythonistas_signup, name='pythonistas_signup'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password/$', pythonista_change_password, name='change_password'),
    url(r'^info/$', pythonista_change_info, name='change_info'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'pythonistas-area-password-change.html'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
] + static(STATIC_URL, document_root=STATIC_ROOT)
