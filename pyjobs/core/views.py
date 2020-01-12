import csv
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from datetime import datetime

from pyjobs.core.forms import (
    ContactForm,
    EditProfileForm,
    JobForm,
    RegisterForm,
    JobApplicationForm,
)
from pyjobs.core.models import Job, JobApplication, Profile
from pyjobs.core.filters import JobFilter
from pyjobs.core.utils import generate_thumbnail


def index(request):
    publicly_available_jobs = Job.get_index_display_jobs()

    user_filtered_query_set = JobFilter(request.GET, queryset=publicly_available_jobs)

    context_dict = {
        "publicly_available_jobs": publicly_available_jobs,
        "filter": user_filtered_query_set,
    }

    return render(request, template_name="index.html", context=context_dict)


def jobs(request):
    publicly_available_jobs = Job.get_publicly_available_jobs()

    user_filtered_query_set = JobFilter(request.GET, queryset=publicly_available_jobs)

    paginator = Paginator(user_filtered_query_set.qs, 10)

    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return redirect("/")

    if page_number > paginator.num_pages:
        return redirect("/")

    public_jobs_to_display = paginator.page(page_number)

    context_dict = {
        "publicly_available_jobs": public_jobs_to_display,
        "premium_available_jobs": Job.get_premium_jobs(),
        "pages": paginator.page_range,
        "filter": user_filtered_query_set,
    }

    return render(request, template_name="jobs.html", context=context_dict)


def services_view(request):
    return render(request, template_name="services.html")


def job_creation(request):
    context_dict = {"new_job_form": JobForm}
    return render(request, template_name="job_registration.html", context=context_dict)


def robots_view(request):
    return render(request, template_name="robots.txt")


def job_view(request, pk):
    context = {
        "job": get_object_or_404(Job, pk=pk),
        "logged_in": False,
        "next_job_pk": int(pk) + 1,
        "previous_job_pk": int(pk) - 1,
    }

    context["title"] = context["job"].title
    context["description"] = context["job"].description

    if request.method == "POST":
        context["job"].apply(request.user)  # aplica o usuario
        return redirect("/job/{}/".format(context["job"].pk))

    if request.user.is_authenticated:
        context["applied"] = JobApplication.objects.filter(
            user=request.user, job=context["job"]
        ).exists()
        context["logged_in"] = True

    return render(request, template_name="job_details.html", context=context)


def summary_view(request):
    jobs = Job()
    context = {"jobs": jobs.get_weekly_summary()}
    return render(request, template_name="summary.html", context=context)


def register_new_job(request):
    if request.method != "POST":
        return redirect("/")

    new_job = JobForm(request.POST)
    g_recaptcha_response = request.POST.get("g-recaptcha-response")
    context = {}

    context["message_first"] = "Falha na hora de criar o job"
    context["message_second"] = "Algum campo não foi preenchido corretamente!"

    if new_job.is_valid(g_recaptcha_response):
        context["message_first"] = "Acabamos de mandar um e-mail para vocês!"
        context[
            "message_second"
        ] = "Cheque o e-mail de vocês para saber como alavancar essa vaga!"

        new_job.save()

    return render(request, template_name="generic.html", context=context)


def close_job(request, pk, close_hash):
    job = get_object_or_404(Job, pk=pk)
    if close_hash != job.close_hash():
        raise Http404("No Job matches the given hash.")

    context = {
        "message_first": "Vaga fechada com sucesso!",
        "message_second": job.title,
    }
    job.is_open = False
    job.save()
    return render(request, template_name="generic.html", context=context)


def contact(request):
    context = {"form": ContactForm(request.POST or None)}

    context["message_first"] = "Falha na hora de mandar a mensagem"
    context[
        "message_second"
    ] = "Você preencheu algum campo da maneira errada, tente novamente!"

    recaptcha_response = request.POST.get("g-recaptcha-response")

    if request.method == "POST" and context["form"].is_valid(recaptcha_response):
        context["form"].save()
        context["message_first"] = "Mensagem enviada com sucesso"
        context["message_second"] = "Vá para a home do site!"

    if request.method == "POST":
        return render(request, template_name="generic.html", context=context)

    return render(request, "contact-us.html", context)


@login_required
def pythonistas_area(request):
    return render(request, "pythonistas-area.html")


def pythonistas_signup(request):
    context = {"form": RegisterForm(request.POST or None)}

    if request.method == "POST" and context["form"].is_valid():
        user = context["form"].save()
        login(request, user)
        return redirect("/")

    return render(request, "pythonistas-signup.html", context)


@login_required
def pythonista_change_password(request):
    template_name = "pythonistas-area-password-change.html"
    context = {"form": PasswordChangeForm(request.user)}

    if request.method == "POST":
        if context["form"].is_valid():
            context["form"] = PasswordChangeForm(request.user, request.POST)
            user = context["form"].save()
            context["message"] = "Sua senha foi alterada com sucesso!"
            update_session_auth_hash(request, user)
            return render(request, template_name, context)
        else:
            context["form"] = PasswordChangeForm(request.user, request.POST)
            context["message"] = "Por favor, corrija os erros abaixo."
    return render(request, "pythonistas-area-password-change.html", context)


@login_required
def pythonista_change_info(request):
    profile = request.user.profile
    template = "pythonistas-area-info-change.html"
    context = {"form": EditProfileForm(instance=profile)}

    if request.method == "POST":
        context["form"] = EditProfileForm(instance=profile, data=request.POST)
        if context["form"].is_valid():
            user = context["form"].save()
            context["message"] = "Suas informações foram atualizadas com sucesso!"
            return render(request, template, context)
        else:
            context["message"] = "Por favor, corrija os erros abaixo."
            messages.error(request, "Por favor, corrija os erros abaixo.")

    return render(request, template, context)


def fb_ads_landing(request):
    """
    View to retrieve all user applications to job.
    """
    template = "landing.html"
    return render(request, template)


@login_required
def pythonista_applied_info(request):
    """
    View to retrieve all user applications to job.
    """
    context = {}
    template = "pythonista-applied-jobs.html"
    context["applications"] = JobApplication.objects.filter(user=request.user.pk)
    return render(request, template, context)


class JobsFeed(Feed):
    title = "{} - Sua central de vagas {}".format(
        settings.WEBSITE_NAME, settings.WEBSITE_WORKING_LANGUAGE
    )
    link = "/feed/"
    description = "As últimas vagas {} destacadas no {}".format(
        settings.WEBSITE_WORKING_LANGUAGE, settings.WEBSITE_NAME
    )

    def items(self):
        return Job.get_feed_jobs()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.get_excerpt()

    def item_link(self, item):
        return reverse("job_view", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_at


class PremiumJobsFeed(Feed):
    title = "{} - Sua central de vagas {}".format(
        settings.WEBSITE_NAME, settings.WEBSITE_WORKING_LANGUAGE
    )
    link = "/feed/"
    description = "As últimas vagas {} destacadas no {}".format(
        settings.WEBSITE_WORKING_LANGUAGE, settings.WEBSITE_NAME
    )

    def items(self):
        return Job.get_premium_jobs()

    def item_title(self, item):
        return "{} em {}".format(item.title, item.workplace)

    def item_description(self, item):
        return item.get_excerpt()

    def item_link(self, item):
        return reverse("job_view", args=[item.pk])

    def item_pubdate(self, item):
        return datetime.now()


@login_required
def job_application_challenge_submission(request, pk):
    user_applied = JobApplication.objects.filter(
        job__pk=pk, user__pk=request.user.pk
    ).first()

    if not user_applied or not user_applied.job.is_challenging:
        return redirect("/job/{}/".format(pk))

    form = JobApplicationForm(request.POST or None, instance=user_applied)

    if request.method == "POST" and form.is_valid():
        form.save()

    if user_applied.challenge_response_at is not None:
        context = {
            "message_first": "Seu teste já foi enviado!",
            "message_second": "Recebemos seu teste, aguarde nosso retorno!",
            "message_explaining": "Recebemos seu teste e vamos avaliar!",
        }
        return render(request, template_name="generic.html", context=context)

    return render(
        request,
        template_name="job_challenge.html",
        context={"job": user_applied.job, "form": form},
    )


@staff_member_required
def applied_users_details(request, pk):

    job_info = Job.objects.filter(pk=pk).first()

    return render(
        request,
        template_name="applied_users_details.html",
        context={"rows": JobApplication.objects.filter(job__pk=pk), "job": job_info},
    )


@staff_member_required
def get_job_applications(request, pk):
    users_grades = [
        (
            "job_pk",
            "grade",
            "first_name",
            "last_name",
            "email",
            "github",
            "linkedin",
            "cellphone",
            "email_sent_at",
            "email_sent",
            "challenge_response_at",
            "challenge_response_link",
            "output",
            "comment",
            "output_sent",
        )
    ]

    users_grades += [
        (
            pk,
            job_applicant.user.profile.profile_skill_grade(pk),
            job_applicant.user.first_name,
            job_applicant.user.last_name,
            job_applicant.user.email,
            job_applicant.user.profile.github,
            job_applicant.user.profile.linkedin,
            job_applicant.user.profile.cellphone,
            job_applicant.email_sent_at,
            job_applicant.email_sent,
            job_applicant.challenge_response_at,
            job_applicant.challenge_response_link,
            job_applicant.output,
            job_applicant.comment,
            job_applicant.output_sent,
        )
        for job_applicant in JobApplication.objects.filter(job__pk=pk)
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="job_{}_users.csv"'.format(
        pk
    )
    writer = csv.writer(response)
    writer.writerows(users_grades)

    return response


def thumbnail_view(request, pk):
    job = Job.objects.filter(pk=pk).first()
    im = generate_thumbnail(job=job)

    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")
    return response


def handler_404(request, exception):
    return redirect("/")
