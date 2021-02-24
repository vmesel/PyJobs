from django.contrib import admin
from pyjobs.profiler.models import ProfilerData
from django.utils.translation import gettext_lazy as _

admin.site.register(ProfilerData)
