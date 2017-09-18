from django.conf.urls import url, include
from apps.core.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^cadastro/', cadastrese, name="cadastro_view"),
    url(r'^dashboard/', dashboard, name="dashboard_view"),
    url(
        r'^login/$',
        auth_views.login,
        {"template_name":"login.html"},
        name='login'
    ),
    url(
        r'^logout/$',
        auth_views.logout,
        {'next_page': '/'},
        name='logout'
    ),
]
