from django.contrib import admin
from .models import Partner


class PartnerAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "skills",
        "related_jobs",
    )


admin.site.register(Partner, PartnerAdmin)
