from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from freela.views import ShowAvailableJobs
from pyfreelas.views import *
from rest_framework import routers
from pyfreelas import settings
from django.contrib.staticfiles import views
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'jobs', ShowAvailableJobs)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/jobs/$', ShowAvailableJobs.as_view({'get':'list', 'post': 'create'})),
    url(r'^$', Home.as_view(), name='index'),
    url(r'^cadastre-job/$', CadastreJobFreela.as_view(), name='cadatre_job_freela'),
    url(r'^freelas-disponiveis/$', EncontreJobFreela.as_view(), name='cadatre_job_freela'),
    url(r'^freela-cadastrado/$', SucessoFreela.as_view(), name='sucesso_job'),
    url(r'^job/(?P<pk>\d+)/', JobFreela.as_view(), name='job_url'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += [
#         url(r'^static/(?P<path>.*)$', views.serve),
#     ]
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
