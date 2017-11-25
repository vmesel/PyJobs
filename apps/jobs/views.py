from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.contrib import messages

from apps.jobs.models import Job, InterestedPerson
from apps.jobs.forms import JobForm
from apps.core.models import Company
from apps.core.forms import EditCompanyForm
from apps.jobs.filters import JobFilter


def find_job(request):
    if request.method == "GET":
        jobs = Job.objects.filter(publico=True)
        jobs_filtered = JobFilter(request.GET, queryset=jobs)
        paginator = Paginator(jobs_filtered.qs, 5)
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
            "user": request.user,
            "jobfilter": jobs_filtered.form
        }
        return render(request, "jobs.html", context)


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

    interesse = False
    if request.user.is_authenticated():
        interest = InterestedPerson.objects.filter(usuario=request.user, job=job)
        if request.method == "POST":
            InterestedPerson.objects.create(usuario=request.user, job=job)
            messages.success(request, "Cadastramos seu interesse na vaga com sucesso")

        interesse = interest.exists()

    return render(request, "job.html", {"job": job, "user": request.user, "interest": interesse})
