from django.conf.urls import url
from django.contrib.auth import views as auth_views

from apps.core.views import *

urlpatterns = [
    url(r'^cadastro/', cadastrese, name="cadastro_view"),
    url(r'^dashboard/', dashboard, name="dashboard_view"),
    url(r'^vagas/', vagas, name="vagas_cadastradas"),
    url(r'^job/edit/(?P<pk>\w+)/$', editar_vaga, name="editar_vaga"),
    url(r'^job/del/(?P<pk>\w+)/$', deletar_job, name="deletar_job"),
    url(r'^update/user/', update_user, name="update_user"),
    url(r'^update/profile/', update_profile, name="update_profile"),
    url(r'^update/company/', update_company, name="update_company"),
    url(r'^password/$', change_password, name='change_password'),
    url(r'^generate-token/$', generate_token, name='generate-token'),
    url(
        r'^login/$',
        auth_views.login,
        {"template_name": "login.html"},
        name='login'
    ),
    url(
        r'^logout/$',
        auth_views.logout,
        {'next_page': '/'},
        name='logout'
    ),
]
