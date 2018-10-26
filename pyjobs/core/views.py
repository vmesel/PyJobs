import requests
from decouple import config
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import TemplateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.db import models

from core.models import Job, Profile, JobApplication
from core.forms import JobForm, ContactForm, RegisterForm, EditProfileForm

class Index(ListView):
    template_name = 'index.html'
    model = Job
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['premium_jobs'] = Job.objects.filter(
            premium=True, public=True).order_by('-created_at')[:2]
        return context

    def get_queryset(self):
        queryset = Job.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q)
                | models.Q(workplace__icontains=q)
                | models.Q(description__icontains=q)
                | models.Q(requirements__icontains=q)
            )
        return queryset


class RobotsView(TemplateView):
    template_name = "robots.txt"


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


class SummaryListView(ListView):
    model = Job
    template_name = "summary.html"

    def get_queryset(self):
        today = datetime.today()
        past_date = datetime.today() - timedelta(days=7)

        queryset = Job.objects.filter(
            created_at__gte=past_date,
            created_at__lte=today,
        )
        return queryset


class RegisterJob(LoginRequiredMixin, FormView):
    template_name = 'form_job.html'
    model = Job
    form_class = JobForm
    success_url = reverse_lazy('register_job')
    
    def form_valid(self, form):
        if self.request.recaptcha_is_valid:
            form.save()
            messages.success(self.request, 'Job criado com sucesso')
            return redirect(reverse_lazy('register_job'))

        else:
            self.request.recaptcha_is_valid = False
            messages.error(self.request, 'reCAPTCHA Invalido . Por Favor Verifique .')
            return redirect(reverse_lazy('register_job'))

    
def contact(request):
    context = {}
    context["new_job_form"] = JobForm

    if request.method == "POST":
        form = ContactForm(request.POST or None)
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
        if form.is_valid() and result['success']:
            form.save()
            context["message_first"] = "Mensagem enviada com sucesso",
            context["message_second"] = "Vá para a home do site!"
            return render(
                request,
                template_name = "generic.html",
                context = context
            )
        else:
            context["message_first"] = "Falha na hora de mandar a mensagem",
            context["message_second"] = "Você preencheu algum campo da maneira errada, tente novamente!"
            return render(
                request,
                template_name = "generic.html",
                context=context
            )

    context["form"] = ContactForm

    return render(request, "contact-us.html", context)


class Pythonistas(TemplateView):
    template_name = "pythonistas-area.html"


def pythonistas_signup(request):
    context = {}
    context["new_job_form"] = JobForm

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
            context["form"] = form
            return render(request, "pythonistas-signup.html", context)
    else:
        form = RegisterForm()
        context["form"] = form
        return render(request, "pythonistas-signup.html", context)


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

    context = {}
    context["form"] = form
    context["new_job_form"] = JobForm

    return render(request, 'pythonistas-area-password-change.html', context)


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
        'form': form,
        "new_job_form": JobForm
    })
