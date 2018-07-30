from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from core.models import Job, Profile, JobApplication
from core.forms import JobForm, ContactForm, RegisterForm, EditProfileForm

from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages


from decouple import config
import requests

def index(request):
    paginator = Paginator(Job.get_publicly_available_jobs(), 5)
    page = request.GET.get('page')
    try:
        public_jobs_to_display = paginator.page(page)
    except:
        public_jobs_to_display = paginator.page(1)

    context_dict = {
        "publicly_available_jobs": public_jobs_to_display,
        "premium_available_jobs": Job.get_premium_jobs(),
        "new_job_form": JobForm,
        "pages": paginator.page_range
    }
    return render(request, template_name="index.html", context=context_dict)


def job_view(request, pk):
    context = {
        "job": get_object_or_404(Job, pk=pk),
        "new_job_form": JobForm,
        "logged_in": False,
        "title": get_object_or_404(Job, pk=pk).title
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
            context["job"].apply(request.user) #aplica o usuario
            return redirect('/job/{}/'.format(context["job"].pk))
    return render(request, template_name="job_details.html", context=context)


def summary_view(request):
    jobs = Job()
    context = {"jobs": jobs.get_weekly_summary()}
    return render(request, template_name="summary.html", context=context)

def register_new_job(request):
    if request.method != "POST":
        return redirect('/')
    else:
        new_job = JobForm(request.POST)
        if new_job.is_valid():
            # Begin Captcha validation
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': config('RECAPTCHA_SECRET_KEY'),
                'response': recaptcha_response
            }
            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data = data
            )

            result = r.json()
            if result['success']:
                new_job.save()
                return render(
                    request,
                    template_name = "generic.html",
                    context = {
                        "message_first": "Job criado com sucesso",
                        "message_second": "Vá para a home do site!",
                        "new_job_form": JobForm,
                    }
                )
            else:
                return render(
                    request,
                    template_name = "generic.html",
                    context = {
                        "message_first": "Preencha corretamente o captcha",
                        "message_second": "Você não completou a validação do captcha!",
                        "new_job_form": new_job,
                    }
                )
        else:
            return render(
                request,
                template_name = "generic.html",
                context = {
                    "message_first": "Falha na hora de criar o job",
                    "message_second": "Você preencheu algum campo da maneira errada, tente novamente!",
                    "new_job_form": new_job,
                }
            )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST or None)
        if form.is_valid():
            form.save()
            return render(
                request,
                template_name = "generic.html",
                context = {
                    "message_first": "Mensagem enviada com sucesso",
                    "message_second": "Vá para a home do site!"
                }
            )
        else:
            return render(
                request,
                template_name = "generic.html",
                context = {
                    "message_first": "Falha na hora de mandar a mensagem",
                    "message_second": "Você preencheu algum campo da maneira errada, tente novamente!"
                }
            )
    return render(request, "contact-us.html", {"form": ContactForm})


def pythonistas_area(request):
    return render(request, "pythonistas-area.html")


def pythonistas_signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            profile = Profile(
                user=user,
                github=form.cleaned_data["github"],
                linkedin=form.cleaned_data["linkedin"],
                portfolio=form.cleaned_data["portfolio"],
                cellphone=form.cleaned_data["cellphone"],
            )
            profile.save()
            login(request, user)
            return redirect("/")
        else:
            return render(request, "pythonistas-signup.html", {"form": form})
    else:
        form = RegisterForm()
        return render(request, "pythonistas-signup.html", {"form": form})


def pythonista_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return render(request, 'pythonistas-area-password-change.html', {
                'form': form,
                'message': 'Sua senha foi alterada com sucesso!'
            })
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pythonistas-area-password-change.html', {
        'form': form
    })


def pythonista_change_info(request):
    profile = Profile.objects.filter(user = request.user).first()
    form = EditProfileForm(instance=profile)
    if request.method == 'POST':
        form = EditProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            user = form.save()
            return render(request, 'pythonistas-area-password-change.html', {
                'form': form,
                'message': 'Suas informações foram atualizadas com sucesso!'
            })
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'pythonistas-area-info-change.html', {
        'form': form
    })
