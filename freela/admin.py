from django.contrib import admin
from freela.models import Freela
# Register your models here.

class FreelaAdmin(admin.ModelAdmin):
    list_display = ("empresa", "email_responsavel_empresa", "titulo_do_job", "data_adicionado", "tipo_freela", "publico")


admin.site.register(Freela, FreelaAdmin)
