from __future__ import unicode_literals
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta

from freela.models import Freela, Freelancer
from emailtools.utils import email_sender, empresa_cadastrou_vaga, contato_cadastrado

from django.template import RequestContext
from django.shortcuts import render_to_response

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
        freela = Freela(**detalhes)
        freela.save()
        msg_email = empresa_cadastrou_vaga(detalhes["empresa"], detalhes["titulo_do_job"])

        link_to_approve = "http://localhost:8000/admin/freela/freela/{}/change/".format(freela.id)
        email_sender(detalhes["email_responsavel_empresa"], "Cadastramos sua oportunidade {} no PyFreelas".format(detalhes["titulo_do_job"]), msg_email)
        email_sender("viniciuscarqueijo@gmail.com", "Nova oportunidade no PyFreelas", link_to_approve)
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


class SucessoContato(generic.TemplateView):
    template_name = "sucesso_contato.html"


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
        return render(request, self.template_name, context, RequestContext(request))

    def post(self, request, *args, **kwargs):
        detalhes = {
            'nome': request.POST.get('nome'),
            'email': request.POST.get('email'),
            'portfolio': request.POST.get('portfolio'),
            'job': get_object_or_404(Freela, pk = int(request.POST.get('objpk')))
        }
        Freelancer.objects.create(**detalhes)
        email_pessoa = contato_cadastrado(nome = detalhes["nome"], email = detalhes["email"], portfolio = detalhes["portfolio"], vaga=detalhes["job"].titulo_do_job, empresa=False)
        email_empresa = contato_cadastrado(nome = detalhes["nome"], email = detalhes["job"], portfolio = detalhes["portfolio"], vaga=detalhes["job"].titulo_do_job, empresa=True)

        email_sender(detalhes["email"], "PyFreelas: Recebemos o seu formulário de interesse na vaga", email_pessoa) # Email para interessado
        print("Enviamos o seu interesse na vaga para a empresa - Email da Pessoa OK")
        email_sender(detalhes["job"].email_responsavel_empresa, "PyFreelas: Você recebeu um interessado na sua vaga", email_empresa) # Email para a empresa
        print("Recebemos um interessado na sua vaga - Email da Empresa OK")
        return redirect('sucesso_contato')
