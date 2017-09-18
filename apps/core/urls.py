from django.conf.urls import url, include
from apps.core.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^cadastro/', cadastrese, name="cadastro_view"),
    url(r'^dashboard/', dashboard, name="dashboard_view"),
    url(r'^update/user/', update_user, name="update_user"),
    url(r'^update/profile/', update_profile, name="update_profile"),
    url(r'^update/company/', update_company, name="update_company"),
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
