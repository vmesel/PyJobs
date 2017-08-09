from __future__ import unicode_literals
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta

from freela.models import Freela, Freelancer
from emailtools.utils import email_sender

class Home(generic.TemplateView):
    template_name = "index.html"


class EncontreJobFreela(generic.TemplateView):
    template_name = "encontre_job_freela.html"

    def get(self, request,  *args, **kwargs):
        # TODO: FAZER FILTRO DE FREELA OU VAGA
        jobs = Freela.objects.filter(tipo_freela=True, publico=True) #.filter(data_adicionado__range=[startdate, enddate])
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


class CadastraOportunidade(generic.TemplateView):
    template_name = "cadastre_job_freela.html"

    def post(self, request, *args, **kwargs):
        detalhes = {
            'empresa': request.POST.get('nome-empresa'),
            'email_responsavel_empresa': request.POST.get('email-empresa'),
            'link_da_empresa': request.POST.get('link-empresa'),
            'titulo_do_job': request.POST.get('titulo-job'),
            'descricao': request.POST.get('descricao-job'),
            'requisitos': request.POST.get('requisitos-job'),
            'tipo_freela': bool(request.POST.get('tipo-freela')),
            'valor_pago': float(request.POST.get('valor-oportunidade'))
        }
        Freela.objects.create(**detalhes)
        msg_email = empresa_cadastrou_vaga(detalhes["empresa"], detalhes["titulo_do_job"])
        email_sender(detalhes["email_responsavel_empresa"], "Cadastramos sua oportunidade {} no PyFreelas".format(detalhes["titulo_do_job"]), msg_email)
        return redirect('sucesso_job')


class OportunidadesView(generic.TemplateView):
    template_name = "oportunidades.html"

class JobFreela(generic.TemplateView):
    template_name = "pagina-job.html"

    def get(self, request,  *args, **kwargs):
        obj = get_object_or_404(Freela, pk = int(self.kwargs['pk']))
        if obj.tipo_freela == True:
            context = {'job': obj}
            return render_to_response(self.template_name, context)
        else:
            return redirect("/vaga/{}".format(obj.pk))

# ADICIONADA O SISTEMA DE CRIACAO E DIVULGACAO DE VAGAS

class EncontreVaga(generic.TemplateView):
    template_name = "encontre_vaga.html"

    def get(self, request,  *args, **kwargs):
        # TODO: FAZER FILTRO DE FREELA OU VAGA
        jobs = Freela.objects.filter(tipo_freela=False, publico=True) # Filtrar tudo que nao for freela
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


class SucessoVaga(generic.TemplateView):
    template_name = "sucesso_job.html"


class VagaView(generic.TemplateView):
    template_name = "pagina-job.html"

    def get(self, request,  *args, **kwargs):
        obj = get_object_or_404(Freela, pk = int(self.kwargs['pk']))
        if obj.tipo_freela == False:
            context = {'job': obj}
            return render_to_response(self.template_name, context)
        else:
            return redirect("/job/{}".format(obj.pk))


class EnvioInteresse(generic.TemplateView):
    template_name = "envio-oferta.html"

    def get(self, request,  *args, **kwargs):
        obj = get_object_or_404(Freela, pk = int(self.kwargs['pk']))
        context = {"obj": obj}
        return render_to_response(self.template_name, context)

    def post(self, request, *args, **kwargs):
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        portfolio = request.POST.get('portfolio')
        objpk = request.POST.get('objpk')
        obj = get_object_or_404(Freela, pk = int(objpk))
        print(objpk)
        Freelancer.create(nome=nome, email=email, portfolio=portfolio, job=obj)
        context = {"success": "True"}
        return redirect('sucesso_job')
