from django.contrib import admin
from apps.jobs.models import Job, InterestedPerson


class JobAdmin(admin.ModelAdmin):
    list_display = ("empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "home_office", "publico")


admin.site.register(Job, JobAdmin)
admin.site.register(InterestedPerson)
