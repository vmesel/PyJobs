from django.contrib import admin
from django.core.mail import send_mail
from django.utils.html import mark_safe
from datetime import datetime
from pyjobs.core.models import (
    Job,
    JobApplication,
    Profile,
    Skill,
)
from pyjobs.marketing.triggers import (
    send_offer_email_template,
    send_feedback_collection_email,
)
from datetime import datetime
from pyjobs.marketing.newsletter import subscribe_user_to_mailer
from pyjobs.core.email_utils import get_email_with_template
from django.utils.translation import gettext_lazy as _


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
                " ".join(map(str, [_("Teste Técnico da empresa:"), job.company_name])),
                [job_applicant.user.email],
            )

            message.send()

            job_applicant.email_sent = True
            job_applicant.email_sent_at = datetime.now()
            job_applicant.save()


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at", "email_sent", "challenge_response_at")


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company_name",
        "ad_interested",
        "challenge_interested",
        "is_challenging",
        "public",
        "premium",
        "created_at",
        "is_open",
        "consultancy",
        "whatsapp_link",
    )
    readonly_fields = ("get_job_hash",)
    actions = [
        send_email_offer,
        send_feedback_collection,
        update_created_at,
        send_challenge_to_old_applicants,
    ]
    filter_horizontal = ("skills",)
    search_fields = ["title", "company_name"]
    list_per_page = 100

    def get_job_hash(self, job):
        return job.listing_hash()

    def whatsapp_link(self, job):
        try:
            cellphone = job.cellphone.replace("+", "").replace(" ", "").replace("-", "")
            return mark_safe(
                f"""
                <a href='https://web.whatsapp.com/send?phone=55{job.cellphone}&text=Ol%C3%A1%21%0A%0ASou%20o%20Vin%C3%ADcius%20do%20%21%20Tudo%20bem%20contigo%3F%0A%0AEstou%20passando%20aqui%20para%20saber%20se%20voc%C3%AA%20precisa%20de%20alguma%20ajuda%20com%20sua%20vaga%20ou%20quer%20conhecer%20mais%20sobre%20nossas%20solu%C3%A7%C3%B5es%21%0A%0AAbra%C3%A7o%21'>WhatsApp</a>
                """
            )
        except:
            return "Sem WhatsApp"


class ProfileAdmin(admin.ModelAdmin):
    actions = [add_subscriber]


admin.site.register(Job, JobAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Skill)
