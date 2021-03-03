import csv
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from datetime import datetime, timedelta

from pyjobs.core.forms import (
    ContactForm,
    EditProfileForm,
    JobForm,
    RegisterForm,
    JobApplicationForm,
    JobApplicationFeedbackForm,
)
from pyjobs.core.models import Job, JobApplication, Profile, Skill
from pyjobs.core.filters import JobFilter
from pyjobs.core.utils import generate_thumbnail
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate
from social_django.models import UserSocialAuth

try:
    CURRENT_DOMAIN = Site.objects.get_current().domain
except:
    CURRENT_DOMAIN = "pyjobs.com.br"

WEBPUSH_CONTEXT = {"group": "general"}


def index(request):
    publicly_available_jobs = Job.get_index_display_jobs()

    user_filtered_query_set = JobFilter(request.GET, queryset=publicly_available_jobs)

    context_dict = {
        "publicly_available_jobs": publicly_available_jobs,
        "filter": user_filtered_query_set,
        "webpush": WEBPUSH_CONTEXT,
    }

    return render(request, template_name="index.html", context=context_dict)


def privacy(request):
    return render(
        request,
        template_name="privacy_policy.html",
        context={"webpush": WEBPUSH_CONTEXT},
    )


def jobs(request):
    publicly_available_jobs = Job.get_publicly_available_jobs()
    publicly_available_premium_jobs = Job.get_premium_jobs()

    user_filtered_query_set = JobFilter(request.GET, queryset=publicly_available_jobs)
    premium_filtered_query_set = JobFilter(
        request.GET, queryset=publicly_available_premium_jobs
    )

    paginator = Paginator(user_filtered_query_set.qs, 10)
    premium_paginator = Paginator(premium_filtered_query_set.qs, 10)

    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return redirect("/")

    if page_number > paginator.num_pages:
        return redirect("/")

    public_jobs_to_display = paginator.page(page_number)
    premium_jobs_to_display = premium_paginator.page(1)

    context_dict = {
        "publicly_available_jobs": public_jobs_to_display,
        "premium_available_jobs": premium_jobs_to_display,
        "pages": paginator.page_range,
        "filter": user_filtered_query_set,
        "webpush": WEBPUSH_CONTEXT,
    }

    return render(request, template_name="jobs.html", context=context_dict)


def job_state_view(request, state):
    states = {
        "acre": (0, "Acre"),
        "alagoas": (1, "Alagoas"),
        "amapa": (2, "Amapá"),
        "amazonas": (3, "Amazonas"),
        "bahia": (4, "Bahia"),
        "ceara": (5, "Ceará"),
        "distrito-federal": (6, "Distrito Federal"),
        "espirito-santo": (7, "Espírito Santo"),
        "goias": (8, "Goiás"),
        "maranhao": (9, "Maranhão"),
        "mato-grosso": (10, "Mato Grosso"),
        "mato-grosso-do-sul": (11, "Mato Grosso do Sul"),
        "minas-gerais": (12, "Minas Gerais"),
        "para": (13, "Pará"),
        "paraiba": (14, "Paraíba"),
        "parana": (15, "Paraná"),
        "pernambuco": (16, "Pernambuco"),
        "piaui": (17, "Piauí"),
        "rio-de-janeiro": (18, "Rio de Janeiro"),
        "rio-grande-do-norte": (19, "Rio Grande do Norte"),
        "rio-grande-do-sul": (20, "Rio Grande do Sul"),
        "rondonia": (21, "Rondônia"),
        "roraima": (22, "Roraima"),
        "santa-catarina": (23, "Santa Catarina"),
        "sao-paulo": (24, "São Paulo"),
        "sergipe": (25, "Sergipe"),
        "tocantins": (26, "Tocantins"),
    }

    if state not in states.keys():
        return redirect("/")

    publicly_available_jobs = Job.get_publicly_available_jobs().filter(
        state=states[state][0]
    )
    publicly_available_premium_jobs = Job.get_premium_jobs().filter(
        state=states[state][0]
    )

    paginator = Paginator(publicly_available_jobs, 10)
    premium_paginator = Paginator(publicly_available_premium_jobs, 10)

    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return redirect("/")

    if page_number > paginator.num_pages:
        return redirect("/")

    public_jobs_to_display = paginator.page(page_number)
    premium_jobs_to_display = premium_paginator.page(1)

    context_dict = {
        "publicly_available_jobs": public_jobs_to_display,
        "premium_available_jobs": premium_jobs_to_display,
        "pages": paginator.page_range,
        "state": states[state][1],
        "webpush": WEBPUSH_CONTEXT,
    }

    return render(
        request,
        template_name="jobs_by_location.html",
        context=context_dict,
    )


def services_view(request):
    return render(
        request,
        template_name="services.html",
        context={"webpush": WEBPUSH_CONTEXT},
    )


def job_creation(request):
    context_dict = {"new_job_form": JobForm, "webpush": WEBPUSH_CONTEXT}
    return render(
        request,
        template_name="job_registration.html",
        context=context_dict,
    )


def robots_view(request):
    return render(request, template_name="robots.txt")


def job_view(request, unique_slug):
    job = get_object_or_404(Job, unique_slug=unique_slug)
    context = {
        "job": job,
        "logged_in": False,
        "next_job_pk": int(job.pk) + 1,
        "previous_job_pk": int(job.pk) - 1,
        "webpush": WEBPUSH_CONTEXT,
    }
    if context["job"].salary_range != 10:
        salaries = (
            str(context["job"].get_salary_range_display())
            .replace(".", "")
            .replace(",", ".")
            .split(" - ")
        )
        if len(salaries) == 2:
            context["salary"] = (salaries[0], salaries[1])
        else:
            context["salary"] = (salaries[0].replace(" +", ""), "30000.00")

    context["valid_thru"] = context["job"].created_at + timedelta(days=60)

    context["too_old"] = False if context["valid_thru"] > datetime.today() else True

    context["title"] = context["job"].title
    context["description"] = context["job"].description

    context["similar_jobs"] = (
        Job.objects.filter(
            Q(skills__in=context["job"].skills.all()),
            ~Q(id=context["job"].id),
            Q(created_at__gt=datetime.now() - timedelta(days=30)),
        )
        .annotate(num_skills=Count("skills"))
        .order_by("-num_skills")[:3]
    )

    if request.method == "POST":
        context["job"].apply(request.user)
        return redirect("/job/{}/".format(context["job"].unique_slug))

    if request.user.is_authenticated:
        context["applied"] = JobApplication.objects.filter(
            user=request.user, job=context["job"]
        ).exists()
        context["logged_in"] = True

    return render(request, template_name="job_details.html", context=context)


def summary_view(request):
    jobs = Job()
    context = {"jobs": jobs.get_weekly_summary(), "webpush": WEBPUSH_CONTEXT}
    return render(request, template_name="summary.html", context=context)


def register_new_job(request):
    if request.method != "POST":
        return redirect("/")

    new_job = JobForm(request.POST)
    g_recaptcha_response = request.POST.get("g-recaptcha-response")
    context = {"webpush": WEBPUSH_CONTEXT}

    context["message_first"] = _("Falha na hora de criar o job")
    context["message_second"] = _("Algum campo não foi preenchido corretamente!")

    if new_job.is_valid(g_recaptcha_response):
        context["message_first"] = _("Acabamos de mandar um e-mail para vocês!")
        context["message_second"] = _(
            "Cheque o e-mail de vocês para saber como alavancar essa vaga!"
        )

        new_job.save()

    return render(request, template_name="generic.html", context=context)


def close_job(request, unique_slug, close_hash):
    job = get_object_or_404(Job, unique_slug=unique_slug)
    if close_hash != job.close_hash():
        raise Http404(_("No Job matches the given hash."))

    context = {
        "message_first": _("Vaga fechada com sucesso!"),
        "message_second": job.title,
        "webpush": WEBPUSH_CONTEXT,
    }
    job.is_open = False
    job.save()
    return render(request, template_name="generic.html", context=context)


def applied_users_details(request, unique_slug):
    job_info = get_object_or_404(Job, unique_slug=unique_slug)

    job_hash = request.GET.get("job_hash")
    job_hash = job_hash == job_info.listing_hash()

    if request.user.is_staff or job_hash:
        return render(
            request,
            template_name="applied_users_details.html",
            context={
                "rows": JobApplication.objects.filter(job__unique_slug=unique_slug),
                "job": job_info,
                "is_staff": request.user.is_staff,
                "webpush": WEBPUSH_CONTEXT,
            },
        )

    return redirect("/")


def contact(request):
    context = {"form": ContactForm(request.POST or None)}

    context["message_first"] = _("Falha na hora de mandar a mensagem")
    context["message_second"] = _(
        "Você preencheu algum campo da maneira errada, tente novamente!"
    )

    recaptcha_response = request.POST.get("g-recaptcha-response")

    if request.method == "POST" and context["form"].is_valid(recaptcha_response):
        context["form"].save()
        context["message_first"] = _("Mensagem enviada com sucesso")
        context["message_second"] = _("Vá para a home do site!")

    context["webpush"] = WEBPUSH_CONTEXT

    if request.method == "POST":
        return render(request, template_name="generic.html", context=context)

    return render(request, "contact-us.html", context)


@login_required
def pythonistas_area(request):
    return render(request, "pythonistas-area.html")


def pythonistas_signup(request):
    context = {"form": RegisterForm(request.POST or None)}
    context["webpush"] = WEBPUSH_CONTEXT

    if request.method == "POST" and context["form"].is_valid():
        user = context["form"].save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("/")

    return render(request, "pythonistas-signup.html", context)


@login_required
def pythonista_change_password(request):
    template_name = "pythonistas-area-password-change.html"
    if request.user.has_usable_password():
        form = PasswordChangeForm
    else:
        form = AdminPasswordChangeForm

    context = {}
    context["form"] = form(request.user)
    context["webpush"] = WEBPUSH_CONTEXT

    if request.method == "POST":
        if context["form"].is_valid():
            context["form"] = form(request.user, request.POST)
            user = context["form"].save()
            context["message"] = _("Sua senha foi alterada com sucesso!")
            update_session_auth_hash(request, user)
            return render(request, template_name, context)
        else:
            context["form"] = form(request.user, request.POST)
            context["message"] = _("Por favor, corrija os erros abaixo.")
    return render(request, "pythonistas-area-password-change.html", context)


@login_required
def pythonista_change_info(request):
    profile = request.user.profile
    template = "pythonistas-area-info-change.html"
    context = {"form": EditProfileForm(instance=profile)}
    context["webpush"] = WEBPUSH_CONTEXT

    if request.method == "POST":
        context["form"] = EditProfileForm(instance=profile, data=request.POST)
        if context["form"].is_valid():
            user = context["form"].save()
            context["message"] = _("Suas informações foram atualizadas com sucesso!")
            return render(request, template, context)
        else:
            context["message"] = _("Por favor, corrija os erros abaixo.")
            messages.error(request, _("Por favor, corrija os erros abaixo."))

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
    context["webpush"] = WEBPUSH_CONTEXT
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
def job_application_challenge_submission(request, unique_slug):
    user_applied = JobApplication.objects.filter(
        job__unique_slug=unique_slug, user__pk=request.user.pk
    ).first()

    if not user_applied or not user_applied.job.is_challenging:
        return redirect("/job/{}/".format(unique_slug))

    form = JobApplicationForm(request.POST or None, instance=user_applied)

    if request.method == "POST" and form.is_valid():
        form.save()

    if user_applied.challenge_response_at is not None:
        context = {
            "message_first": _("Seu teste já foi enviado!"),
            "message_second": _("Recebemos seu teste, aguarde nosso retorno!"),
            "message_explaining": _("Recebemos seu teste e vamos avaliar!"),
        }
        return render(request, template_name="generic.html", context=context)

    return render(
        request,
        template_name="job_challenge.html",
        context={"job": user_applied.job, "form": form},
    )


@staff_member_required
def get_job_applications(request, unique_slug):
    job = get_object_or_404(Job, unique_slug=unique_slug)
    users_grades = [
        (
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
            job_applicant.user.profile.profile_skill_grade(job.pk),
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
        for job_applicant in JobApplication.objects.filter(job__unique_slug=unique_slug)
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="job_{}_users.csv"'.format(
        unique_slug
    )
    writer = csv.writer(response)
    writer.writerows(users_grades)

    return response


def thumbnail_view(request, unique_slug):
    job = Job.objects.filter(unique_slug=unique_slug).first()
    im = generate_thumbnail(job=job)

    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")
    return response


def handler_404(request, exception):
    return redirect("/")


def handler_500(request, *args, **kwargs):
    response = render(
        request,
        "generic.html",
        context={
            "message_first": str(_("Oops... Passamos vergonha agora! =P")),
            "message_second": str(
                _(
                    "Já mandamos o erro que acabou de acontecer contigo ao administrador!"
                )
            ),
            "message_explaining": str(
                _(
                    "De vez em quando nós também erramos, esperamos que você não fique chateado e volte ao nosso site"
                )
            ),
        },
    )
    response.status_code = 500
    return response


def job_application_feedback(request, pk):
    job_application = get_object_or_404(JobApplication, pk=pk)
    feedback_form = JobApplicationFeedbackForm(
        request.POST or None, instance=job_application
    )

    context = {"job_application": job_application, "feedback_form": feedback_form}

    if request.method == "POST" and feedback_form.is_valid():
        feedback_form.save()

    return render(request, "job_application_feedback.html", context)


def job_skill_view(request, unique_slug):
    """
    This view will return jobs related to a certain skill,
    i.e., Django Jobs or Flask Jobs.
    """
    skill = Skill.objects.filter(unique_slug=unique_slug).first()

    if not skill:
        return redirect("/")

    publicly_available_jobs = Job.get_publicly_available_jobs().filter(skills=skill)
    publicly_available_premium_jobs = Job.get_premium_jobs().filter(skills=skill)

    paginator = Paginator(publicly_available_jobs, 10)
    premium_paginator = Paginator(publicly_available_premium_jobs, 10)

    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return redirect("/")

    if page_number > paginator.num_pages:
        return redirect("/")

    public_jobs_to_display = paginator.page(page_number)
    premium_jobs_to_display = premium_paginator.page(1)

    context_dict = {
        "publicly_available_jobs": public_jobs_to_display,
        "premium_available_jobs": premium_jobs_to_display,
        "pages": paginator.page_range,
        "skill": skill,
        "webpush": WEBPUSH_CONTEXT,
    }

    return render(
        request,
        template_name="jobs_by_skill.html",
        context=context_dict,
    )
