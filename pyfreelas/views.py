from __future__ import unicode_literals
from django.views import generic
from django.views.generic import CreateView
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta

from freela.models import Freela, Freelancer
from freela.forms import FreelaForm, FreelancerForm
from emailtools.utils import email_sender, empresa_cadastrou_vaga, contato_cadastrado

from django.template import RequestContext
from django.shortcuts import render_to_response


def home_view(request):
    return render(request, "index.html")


def find_job(request):
    if request.method == "GET":
        jobs = Freela.objects.filter(publico=True)
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
        context = {'jobs': jobs_pag, 'pages': paginator.page_range, 'actual_page': int(page)}
        return render(request, "jobs.html", context)


def create_job(request):
    template_name = "cadastro.html"
    form = FreelaForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            # Passar logica para model
            # msg_email = empresa_cadastrou_vaga(form.cleaned_data["empresa"], form.cleaned_data["titulo_do_job"])
            # email_sender(form.cleaned_data["email_responsavel_empresa"],  "Cadastramos sua oportunidade {} no PyFreelas".format(form.cleaned_data["titulo_do_job"]), msg_email)
            # email_sender("viniciuscarqueijo@gmail.com",  "Nova vaga cadastrada", "http://www.pyfreelas.com.br/admin/freela/freela/{}/change".format(self.object.pk))
            messages.success(request, 'Job Cadastrado com Sucesso!')

    return render(request, template_name, {"form": form})


def job_info(request, pk):
    job = get_object_or_404(Freela, pk = int(pk))
    form = FreelancerForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            insert_dict = {
                "nome": request.POST.get("nome"),
                "email": request.POST.get("email"),
                "portfolio":  request.POST.get("portfolio"),
                "job": job
            }
            Freelancer.objects.create(**insert_dict)
            messages.success(request, 'Contato Cadastrado com Sucesso!')

    return render(request, "job.html", { "job" : job, "form" : form })


#  Passar logica para Model
#         email_pessoa = contato_cadastrado(nome = form.cleaned_data["nome"], email = form.cleaned_data["email"], portfolio = form.cleaned_data["portfolio"], vaga=job.titulo_do_job, empresa=False)
#         email_empresa = contato_cadastrado(nome = form.cleaned_data["nome"], email = job.email_responsavel_empresa, portfolio = form.cleaned_data["portfolio"], vaga=job.titulo_do_job, empresa=True)
#
#         email_sender(form.cleaned_data["email"], "PyFreelas: Recebemos o seu contato!", email_pessoa)
#         email_sender(job.email_responsavel_empresa, "PyFreelas: Recebemos um interessado em sua vaga!", email_empresa)
