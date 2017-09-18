from django.contrib import admin
from apps.jobs.models import Job, InterestedPerson
# Register your models here.

class JobAdmin(admin.ModelAdmin):
    list_display = ("empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "publico")


admin.site.register(Job, JobAdmin)
admin.site.register(InterestedPerson)
