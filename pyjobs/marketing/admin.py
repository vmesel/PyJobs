from django.contrib import admin
from .models import Contact, Messages, MailingList, Share


class MailingListsAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "slug")


class SharingAdmin(admin.ModelAdmin):
    list_display = ("user_sharing", "user_receiving_email", "job")


class MessagesAdmin(admin.ModelAdmin):
    list_display = ("message_title", "message_type")


admin.site.register(Contact)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(MailingList, MailingListsAdmin)
admin.site.register(Share, SharingAdmin)
