from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin

from apps.jobs.urls import *
# from rest_framework import routers
from pyjobs import settings
from pyjobs.views import *

urlpatterns = [
                  # Default URLs
                  url(r'^$', home_view, name='index'),
                  url(r'^admin/', admin.site.urls),

                  url(r'^', include('apps.jobs.urls', namespace='jobs')),
                  url(r'^', include('apps.core.urls', namespace='core')),
                  url(r'^cvdb/', include('apps.curriculumdb.urls', namespace='curriculumdb')),
                  url('^', include('django.contrib.auth.urls')),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
