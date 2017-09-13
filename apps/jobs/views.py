# from django.shortcuts import render
# from __future__ import unicode_literals
from django.views import generic
from django.views.generic import CreateView
from django.http import JsonResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta

from apps.jobs.models import Job, Person
from apps.jobs.forms import JobForm, PersonForm

from django.template import RequestContext
from django.shortcuts import render_to_response

def find_job(request):
    if request.method == "GET":
        jobs = Job.objects.filter(publico=True)
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
        context = {'jobs': jobs_pag, 'pages': paginator.page_range, 'actual_page': int(page), 'n_pages': int(paginator.num_pages)}
        return render(request, "jobs.html", context)


def create_job(request):
    template_name = "cadastro.html"
    form = JobForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Job Cadastrado com Sucesso!')

    return render(request, template_name, {"form": form})


def job_info(request, pk):
    job = get_object_or_404(Job, pk = int(pk))
    form = PersonForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            insert_dict = {
                "nome": request.POST.get("nome"),
                "email": request.POST.get("email"),
                "portfolio":  request.POST.get("portfolio"),
                "job": job
            }
            Person.objects.create(**insert_dict)
            messages.success(request, 'Contato Cadastrado com Sucesso!')

    return render(request, "job.html", { "job" : job, "form" : form })
