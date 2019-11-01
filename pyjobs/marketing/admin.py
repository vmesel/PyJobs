from django.contrib import admin
from .models import Contact, Messages, MailingList


class MailingListsAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "slug")


admin.site.register(Contact)
admin.site.register(Messages)
admin.site.register(MailingList, MailingListsAdmin)
