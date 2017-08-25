from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from pyfreelas.views import *
from rest_framework import routers
from pyfreelas import settings
from django.contrib.staticfiles import views
from django.conf.urls.static import static

urlpatterns = [
    # Default URLs
    url(r'^$', home_view, name='index'),
    url(r'^admin/', admin.site.urls),

    url(r'^jobs/$', find_job, name='cadatre_job_freela'),
    url(r'^cadastro-job/$', create_job, name='cadatre_job_freela'),
    url(r'^job/(?P<pk>\d+)/', job_info, name='job_url'),

    # url(r'^freela-cadastrado/$', SucessoFreela.as_view(), name='sucesso_job'),
    # url(r'^contato-cadastrado/$', SucessoContato.as_view(), name='sucesso_contato'),
    #
    # url(r'^envio-interesse/(?P<pk>\d+)/', EnvioInteresse.as_view(), name='envio_interesse'),
    # url(r'^envio-interesse/', EnvioInteresse.as_view(), name='envio_interesse'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG == False:
#     urlpatterns += [
#         url(r'^static/(?P<path>.*)$', views.serve),
#     ]
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
