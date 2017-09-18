from django.views import generic
from django.views.generic import CreateView
from django.http import JsonResponse

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
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from apps.core.models import Skills, Company
from apps.core.forms import *


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
                user.save()
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
