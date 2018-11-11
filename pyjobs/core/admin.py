from django.contrib import admin
from core.models import Job, Profile, JobApplication, Contact, Messages, send_offer_email_template
from django.core.mail import send_mail

def send_email_offer(modeladmin, request, queryset):
    for j in queryset:
        send_offer_email_template(j)

class JobAdmin(admin.ModelAdmin):
    actions = [send_email_offer]

admin.site.register(Job, JobAdmin)
admin.site.register(Profile)
admin.site.register(JobApplication)
admin.site.register(Contact)
admin.site.register(Messages)
