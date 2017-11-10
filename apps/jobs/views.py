from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView

from apps.jobs.models import Job, InterestedPerson
from apps.jobs.forms import JobForm
from apps.core.models import Company
from apps.core.forms import EditCompanyForm

from watson import search as watson


class JobListView(ListView):

    context_object_name = 'jobs'
    template_name = 'jobs.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = Job.objects.filter(publico=True)
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset = watson.filter(queryset, q)
        return queryset


def create_job(request):
    template_name = "cadastro.html"
    if request.user.is_authenticated():
        context = {}
        if Company.objects.filter(usuario=request.user).count() == 1:
            context["form"] = JobForm(request.POST or None)
            context["company_user"] = True
        else:
            context["company_user"] = False
            context["form"] = EditCompanyForm(request.POST)

        form = context["form"]

        if request.method == "POST":
            if form.is_valid():
                if context["company_user"]:
                    form_data = {
                        "titulo_do_job": form.cleaned_data.get("titulo_do_job"),
                        "home_office": form.cleaned_data.get("home_office"),
                        "descricao": form.cleaned_data.get("descricao"),
                        "requisitos": form.cleaned_data.get("requisitos"),
                        "local": form.cleaned_data.get("local"),
                        "tipo_freela": form.cleaned_data.get("tipo_freela"),
                        "empresa": request.user.company
                    }
                    Job.objects.create(**form_data)
                    messages.success(request, 'Job Cadastrado com Sucesso!')
                else:
                    form_data = {
                        "nome": form.cleaned_data.get("nome"),
                        "email": form.cleaned_data.get("email"),
                        "site": form.cleaned_data.get("site"),
                        "descricao": form.cleaned_data.get("descricao"),
                        "usuario": request.user
                    }

                    Company.objects.create(**form_data)
                    messages.success(request, 'Empresa Cadastrada com Sucesso!')
                form.clean()
    else:
        form = []

    return render(request, template_name, {"form": form, "user": request.user})


def job_info(request, pk):
    job = get_object_or_404(Job, pk=int(pk))

    if request.user.is_authenticated():
        interest = InterestedPerson.objects.filter(usuario=request.user, job=job)
        if request.method == "POST":
            InterestedPerson.objects.create(usuario=request.user, job=job)
            messages.success(request, "Cadastramos seu interesse na vaga com sucesso")

        interesse = interest.exists()

    interesse = False
    return render(request, "job.html", {"job": job, "user": request.user, "interest": interesse})
