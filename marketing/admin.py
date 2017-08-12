from django.contrib import admin
from marketing.models import Prospect

# Register your models here.
class ProspectAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "empresa_ou_pessoa")

admin.site.register(Prospect, ProspectAdmin)
