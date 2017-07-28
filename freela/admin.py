from django.contrib import admin
from freela.models import Freela
# Register your models here.

class FreelaAdmin(admin.ModelAdmin):
    list_display = ("empresa", "email_responsavel_empresa", "titulo_do_job", "descricao", "data_adicionado")


admin.site.register(Freela, FreelaAdmin)
