from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from pyjobs.views import *
from apps.jobs.urls import *
from rest_framework import routers
from pyjobs import settings
from django.contrib.staticfiles import views
from django.conf.urls.static import static

urlpatterns = [
    # Default URLs
    url(r'^$', home_view, name='index'),
    url(r'^admin/', admin.site.urls),

    url(r'^', include('apps.jobs.urls', namespace='jobs')),
    url(r'^', include('apps.core.urls', namespace='core')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
