from django.contrib import admin
from apps.jobs.models import Freela, Freelancer
# Register your models here.

class FreelaAdmin(admin.ModelAdmin):
    list_display = ("empresa", "email_responsavel_empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "publico")


class FreelancersAdmin(admin.ModelAdmin):
    list_display = ("nome", "get_job", "email")

    def get_job(self, obj):
        return obj.job.titulo_do_job

admin.site.register(Freela, FreelaAdmin)
admin.site.register(Freelancer, FreelancersAdmin)
