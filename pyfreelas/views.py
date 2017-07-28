from __future__ import unicode_literals
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta

from freela.models import Freela


class Home(generic.TemplateView):
    template_name = "index.html"


class EncontreJobFreela(generic.TemplateView):
    template_name = "encontre_job_freela.html"

    def get(self, request,  *args, **kwargs):
        enddate = date.today()
        startdate = enddate - timedelta(days=30)
        jobs = Freela.objects.all() #.filter(data_adicionado__range=[startdate, enddate])

        # jobs = Freela.objects.all()
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
        return render_to_response(self.template_name, context)

class SucessoFreela(generic.TemplateView):
    template_name = "sucesso_job.html"

class CadastreJobFreela(generic.TemplateView):
    template_name = "cadastre_job_freela.html"

    def post(self, request, *args, **kwargs):
        detalhes = {
            'empresa': request.POST.get('nome-empresa'),
            'email_responsavel_empresa': request.POST.get('email-empresa'),
            'link_da_empresa': request.POST.get('link-empresa'),
            'titulo_do_job': request.POST.get('titulo-job'),
            'link_job': request.POST.get('link-para-o-job'),
            'descricao': request.POST.get('descricao-job'),
            'requisitos': request.POST.get('requisitos-job'),
        }
        Freela.objects.create(**detalhes)
        return redirect('sucesso_job')

class JobFreela(generic.TemplateView):
    template_name = "pagina-job.html"

    def get(self, request,  *args, **kwargs):
        obj = get_object_or_404(Freela, pk = int(self.kwargs['pk']))
        context = {'job': obj}
        return render_to_response(self.template_name, context)
