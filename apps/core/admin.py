from django.contrib import admin
from apps.core.models import Profile, Company

# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ("empresa", "email_responsavel_empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "publico")
#
#
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ("nome", "get_job", "email")
#
#     def get_job(self, obj):
#         return obj.job.titulo_do_job

admin.site.register(Profile) # , ProfileAdmin)
admin.site.register(Company) # , CompanyAdmin)
