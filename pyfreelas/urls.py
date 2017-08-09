from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from pyfreelas.views import *
from rest_framework import routers
from pyfreelas import settings
from django.contrib.staticfiles import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', Home.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^cadastre-oportunidade/$', CadastraOportunidade.as_view(), name='cadatre_job_freela'),
    url(r'^oportunidades/$', OportunidadesView.as_view(), name='oportunidades'),
    url(r'^freelas-disponiveis/$', EncontreJobFreela.as_view(), name='cadatre_job_freela'),
    url(r'^vagas-disponiveis/$', EncontreVaga.as_view(), name='cadatre_vaga'),
    url(r'^freela-cadastrado/$', SucessoFreela.as_view(), name='sucesso_job'),

    url(r'^job/(?P<pk>\d+)/', JobFreela.as_view(), name='job_url'),
    url(r'^vaga/(?P<pk>\d+)/', VagaView.as_view(), name='vaga_url'),
    url(r'^envio-interesse/(?P<pk>\d+)/', EnvioInteresse.as_view(), name='envio_interesse'),
    url(r'^envio-interesse-form/', EnvioFormInteresse.as_view(), name='envio_interesse_parte2'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG == False:
#     urlpatterns += [
#         url(r'^static/(?P<path>.*)$', views.serve),
#     ]
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
