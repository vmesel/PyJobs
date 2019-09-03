from django.contrib import admin
from django.core.mail import send_mail
from datetime import datetime
from pyjobs.core.models import (
    Contact,
    Job,
    JobApplication,
    Messages,
    Profile,
    Skill,
    MailingList,
    send_offer_email_template,
    send_feedback_collection_email,
)
from pyjobs.core.newsletter import subscribe_user_to_mailer

def update_created_at(modeladmin, request, queryset):
    for i in queryset:
        i.created_at = datetime.now()

def send_email_offer(modeladmin, request, queryset):
    for j in queryset:
        send_offer_email_template(j)


def send_feedback_collection(modeladmin, request, queryset):
    for j in queryset:
        send_feedback_collection_email(j)


def add_subscriber(modeladmin, request, queryset):
    for prof in queryset:
        subscribe_user_to_mailer(prof)


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")


class MailingListsAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "slug")


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company_name",
        "ad_interested",
        "public",
        "premium",
        "created_at",
    )
    actions = [send_email_offer, send_feedback_collection]
    search_fields = ["title", "company_name"]
    list_per_page = 100


class ProfileAdmin(admin.ModelAdmin):
    actions = [add_subscriber]


admin.site.register(Job, JobAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Contact)
admin.site.register(Messages)
admin.site.register(Skill)
admin.site.register(MailingList, MailingListsAdmin)
