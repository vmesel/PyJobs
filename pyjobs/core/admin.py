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
from datetime import datetime
from pyjobs.core.newsletter import subscribe_user_to_mailer
from pyjobs.core.email_utils import get_email_with_template


def update_created_at(modeladmin, request, queryset):
    for i in queryset:
        i.created_at = datetime.now()
        i.save()


def send_email_offer(modeladmin, request, queryset):
    for j in queryset:
        send_offer_email_template(j)


def send_feedback_collection(modeladmin, request, queryset):
    for j in queryset:
        send_feedback_collection_email(j)


def add_subscriber(modeladmin, request, queryset):
    for prof in queryset:
        subscribe_user_to_mailer(prof)


def send_challenge_to_old_applicants(modeladmin, request, queryset):
    available_jobs = [job for job in queryset if job.is_challenging]

    emails_to_be_sent = []

    for job in available_jobs:

        job_applicantions = JobApplication.objects.filter(job=job, email_sent=False)

        for job_applicant in job_applicantions:
            email_context = {
                "vaga": job,
                "pessoa": job_applicant.user.profile,
                "mensagem": job_applicant,
            }

            message = get_email_with_template(
                "job_interest_challenge",
                email_context,
                "Teste Técnico da empresa: {}!".format(job.company_name),
                [job_applicant.user.email],
            )

            message.send()

            job_applicant.email_sent = True
            job_applicant.email_sent_at = datetime.now()
            job_applicant.save()


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "job",
        "created_at",
        "email_sent",
        "challenge_response_at"
    )


class MailingListsAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "slug")


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company_name",
        "ad_interested",
        "challenge_interested",
        "public",
        "premium",
        "created_at",
        "is_open",
    )
    actions = [
        send_email_offer,
        send_feedback_collection,
        update_created_at,
        send_challenge_to_old_applicants,
    ]
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
