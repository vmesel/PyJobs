from django.contrib import admin
from core.models import \
    (
        Job, Profile, JobApplication,
        Contact, Messages, send_offer_email_template,
        Skills
    )
from django.core.mail import send_mail
from core.newsletter import subscribe_user_to_chimp

def send_email_offer(modeladmin, request, queryset):
    for j in queryset:
        send_offer_email_template(j)

def add_subscriber(modeladmin, request, queryset):
    for prof in queryset:
        subscribe_user_to_chimp(prof)

class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company_name', 'ad_interested',
        'public', 'premium', 'created_at'
    )
    actions = [send_email_offer]

class ProfileAdmin(admin.ModelAdmin):
    actions = [add_subscriber]

admin.site.register(Job, JobAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(JobApplication)
admin.site.register(Contact)
admin.site.register(Messages)
admin.site.register(Skills)
