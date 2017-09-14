from django.contrib import admin
from apps.jobs.models import Job, Person
# Register your models here.

class JobAdmin(admin.ModelAdmin):
    list_display = ("empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "publico")


class PersonAdmin(admin.ModelAdmin):
    list_display = ("nome", "get_job", "email")

    def get_job(self, obj):
        return obj.job.titulo_do_job

admin.site.register(Job, JobAdmin)
admin.site.register(Person, PersonAdmin)
