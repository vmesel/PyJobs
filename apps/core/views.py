from django.views import generic
from django.views.generic import CreateView
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from apps.core.models import Skills, Company
from apps.jobs.models import Job
from apps.core.forms import *
from apps.jobs.forms import JobForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def cadastrese(request):
    if request.user.is_authenticated():
        return redirect("/dashboard/")
    else:
        template_name = "registrar.html"
        form = CadastreSeForm(request.POST)

        if request.method == "POST":
            if form.is_valid():
                user = form.save()
                user.profile.telefone = form.cleaned_data.get('telefone')
                user.profile.github = form.cleaned_data.get('github')
                user.profile.linkedin = form.cleaned_data.get('linkedin')
                user.profile.portfolio = form.cleaned_data.get('portfolio')
                user.profile.skills = form.cleaned_data.get('skills')
                user.profile.interesse_banco_cv = form.cleaned_data.get('agree_banco_cv', False)
                userform, userpass = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
                user.save()
                new_user = authenticate(
                    username=userform,
                    password=userpass
                )
                login(request, new_user)
                return redirect("/")
        else:
            form = CadastreSeForm()
        context = {
            "form": form,
            "h2": "Cadastre-se e conheça todos os Jobs em Python ou os cadastre",
            "description": "O PyJobs é uma plataforma que permite a qualquer usuário cadastrar jobs e se inscrever a todos que estiverem disponíveis."
        }

        return render(request, template_name, context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('core:dashboard_view')
        else:
            messages.error(request, 'Corrija os erros abaixo')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

@login_required
def dashboard(request):
    user = request.user

    context = {
        "user":request.user,
        "userform": EditUserForm(instance=request.user),
        "profileform": EditProfileForm(instance=request.user.profile),
    }

    if Company.objects.filter(usuario=user).count() == 1:
        context["companyform"] = EditCompanyForm(instance=request.user.company)
        context["company_user"] = True
    else:
        context["company_user"] = False
        context["companyform"] = EditCompanyForm()

    template_name = "dashboard.html"

    return render(request, template_name, context)

@login_required
def update_user(request):
    user = request.user
    form = EditUserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
    messages.success(request, 'Usuário Atualizado com Sucesso!')
    return redirect("/dashboard/")

@login_required
def update_profile(request):
    profile = request.user.profile
    form = EditProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
    messages.success(request, 'Perfil Atualizado com Sucesso!')
    return redirect("/dashboard/")

@login_required
def update_company(request):
    company = request.user.company
    form = EditCompanyForm(request.POST or None, instance=company)
    if form.is_valid():
        form.save()
    messages.success(request, 'Empresa Atualizada com Sucesso!')
    return redirect("/dashboard/")


@login_required
def vagas(request):
    company = Company.objects.get(usuario=request.user)
    jobs = Job.objects.filter(empresa=company)

    paginator = Paginator(jobs, 5)
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        jobs_pag = paginator.page(page)
    except PageNotAnInteger:
        jobs_pag = paginator.page(1)
    except EmptyPage:
        jobs_pag = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs_pag,
        'pages': paginator.page_range,
        'actual_page': int(page),
        'n_pages': int(paginator.num_pages),
        "user":request.user
    }
    return render(request, "jobs-empresa.html", context)

@login_required
def editar_vaga(request, pk):
    template_name = "editar-vaga.html"
    job = Job.objects.get(pk=pk)
    if job.empresa.usuario == request.user:
        form = JobForm(request.POST or None, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Suas alterações foram salvas")
        return render(request, template_name, {"form": form})


@login_required
def deletar_job(request, pk):
    job = Job.objects.get(pk=pk)
    if job.empresa.usuario == request.user:
        job.delete()
        messages.success(request, "Job deletado com sucesso")
        return redirect("core:dashboard_view")
