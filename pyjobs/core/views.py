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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pyjobs.core.forms import ContactForm, EditProfileForm, JobForm, RegisterForm
from pyjobs.core.models import Job, JobApplication, Profile


def index(request):
    search = (
        request.GET.get("search", "")
        if len(request.GET.get("search", "")) > 3
        else None
    )

    paginator = Paginator(Job.get_publicly_available_jobs(search), 7)

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
        "new_job_form": JobForm,
        "pages": paginator.page_range,
        "search": search if search is not None else "",
    }
    return render(request, template_name="index.html", context=context_dict)


def services_view(request):
    context_dict = {"new_job_form": JobForm}
    return render(request, template_name="services.html", context=context_dict)


def robots_view(request):
    return render(request, template_name="robots.txt")


def job_view(request, pk):
    context = {
        "job": get_object_or_404(Job, pk=pk),
        "new_job_form": JobForm,
        "logged_in": False,
        "title": get_object_or_404(Job, pk=pk).title,
    }
    try:
        interest = JobApplication.objects.filter(user=request.user, job=context["job"])
        if interest.exists():
            context["applied"] = True
        else:
            context["applied"] = False
    except:
        pass

    if request.user.is_authenticated():
        context["logged_in"] = True
        if request.method == "POST":
            context["job"].apply(request.user)  # aplica o usuario
            return redirect("/job/{}/".format(context["job"].pk))
    return render(request, template_name="job_details.html", context=context)


def summary_view(request):
    jobs = Job()
    context = {"jobs": jobs.get_weekly_summary()}
    return render(request, template_name="summary.html", context=context)


def register_new_job(request):
    if request.method != "POST":
        return redirect("/")
    else:
        new_job = JobForm(request.POST)
        if new_job.is_valid():
            if settings.RECAPTCHA_SECRET_KEY:
                recaptcha_response = request.POST.get("g-recaptcha-response")
                data = {
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": recaptcha_response,
                }
                r = requests.post(
                    "https://www.google.com/recaptcha/api/siteverify", data=data
                )

                result = r.json()
                if result["success"]:
                    new_job.save()
                    return render(
                        request,
                        template_name="generic.html",
                        context={
                            "message_first": "Acabamos de mandar um e-mail para vocês!",
                            "message_second": "Cheque o e-mail de vocês para saber como alavancar essa vaga!",
                            "new_job_form": JobForm,
                        },
                    )
                else:
                    return render(
                        request,
                        template_name="generic.html",
                        context={
                            "message_first": "Preencha corretamente o captcha",
                            "message_second": "Você não completou a validação do captcha!",
                            "new_job_form": new_job,
                        },
                    )
            else:
                new_job.save()
                return render(
                    request,
                    template_name="generic.html",
                    context={
                        "message_first": "Acabamos de mandar um e-mail para vocês!",
                        "message_second": "Cheque o e-mail de vocês para saber como alavancar essa vaga!",
                        "new_job_form": JobForm,
                    },
                )
        else:
            return render(
                request,
                template_name="generic.html",
                context={
                    "message_first": "Falha na hora de criar o job",
                    "message_second": "Você preencheu algum campo da maneira errada, tente novamente!",
                    "new_job_form": new_job,
                },
            )


def contact(request):
    context = {}
    context["new_job_form"] = JobForm

    if request.method == "POST":
        form = ContactForm(request.POST or None)
        recaptcha_response = request.POST.get("g-recaptcha-response")
        data = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": recaptcha_response}
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()
        if form.is_valid() and result["success"]:
            form.save()
            context["message_first"] = ("Mensagem enviada com sucesso",)
            context["message_second"] = "Vá para a home do site!"
            return render(request, template_name="generic.html", context=context)
        else:
            context["message_first"] = ("Falha na hora de mandar a mensagem",)
            context[
                "message_second"
            ] = "Você preencheu algum campo da maneira errada, tente novamente!"
            return render(request, template_name="generic.html", context=context)

    context["form"] = ContactForm

    return render(request, "contact-us.html", context)


@login_required
def pythonistas_area(request):
    context_dict = {"new_job_form": JobForm}
    return render(request, "pythonistas-area.html", context=context_dict)


def pythonistas_signup(request):
    context = {"new_job_form": JobForm, "form": RegisterForm(request.POST or None)}

    if request.method == "POST" and context["form"].is_valid():
        user = context["form"].save()
        login(request, user)
        return redirect("/")

    return render(request, "pythonistas-signup.html", context)


@login_required
def pythonista_change_password(request):
    template_name = "pythonistas-area-password-change.html"
    context = {"form": PasswordChangeForm(request.user), "new_job_form": JobForm}

    if request.method == "POST":
        if context["form"].is_valid():
            context["form"] = PasswordChangeForm(request.user, request.POST)
            user = context["form"].save()
            context["message"] = "Sua senha foi alterada com sucesso!"
            update_session_auth_hash(request, user)
            return render(request, template_name, context)
        else:
            context["form"] = PasswordChangeForm(request.user, request.POST)
            messages.error(request, "Por favor, corrija os erros abaixo.")
    return render(request, "pythonistas-area-password-change.html", context)


@login_required
def pythonista_change_info(request):
    profile = request.user.profile
    template = "pythonistas-area-info-change.html"
    context = {"form": EditProfileForm(instance=profile), "new_job_form": JobForm}

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


class JobsFeed(Feed):
    title = "PyJobs - Sua central de vagas Python"
    link = "/feed/"
    description = "As últimas vagas Python cadastradas no PyJobs"

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
    title = "PyJobs - Sua central de vagas Python"
    link = "/feed/"
    description = "As últimas vagas Python destacadas no PyJobs"

    def items(self):
        return Job.get_premium_jobs()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.get_excerpt()

    def item_link(self, item):
        return reverse("job_view", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_at


def jooble_feed(request):
    jobs = Job.objects.all()
    return render(
        request, "jooble.xml", context={"jobs": jobs}, content_type="text/xml"
    )


@staff_member_required
def get_job_related_users(request, pk):
    users_grades = [("job_pk", "grade", "user_pk")]
    users_grades += [
        (pk, profile.profile_skill_grade(pk), profile.pk) for profile in Profile.objects.all()
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_{}_users.csv"'.format(pk)
    writer = csv.writer(response)
    writer.writerows(users_grades)

    return response
