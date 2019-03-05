from django.contrib import admin
from django.core.mail import send_mail

from pyjobs.core.models import (
    Contact,
    Job,
    JobApplication,
    Messages,
    Profile,
    Skill,
    send_offer_email_template,
)
from pyjobs.core.newsletter import subscribe_user_to_chimp


def send_email_offer(modeladmin, request, queryset):
    for j in queryset:
        send_offer_email_template(j)


def add_subscriber(modeladmin, request, queryset):
    for prof in queryset:
        subscribe_user_to_chimp(prof)


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company_name",
        "ad_interested",
        "public",
        "premium",
        "created_at",
    )
    actions = [send_email_offer]


class ProfileAdmin(admin.ModelAdmin):
    actions = [add_subscriber]


admin.site.register(Job, JobAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Contact)
admin.site.register(Messages)
admin.site.register(Skill)
