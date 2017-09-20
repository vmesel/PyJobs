from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from apps.core.models import Profile


def has_curriculumdb_plan(view):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.profile.plano_de_cv_db:
                return view(request, *args, **kwargs)
            return redirect("/cadastro-job/")
        else:
            return redirect("/")
    return wrap

@has_curriculumdb_plan
def lista_de_curriculos(request):
    profiles = Profile.objects.filter(interesse_banco_cv=True)
    paginator = Paginator(profiles, 5)
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        cv_pag = paginator.page(page)
    except PageNotAnInteger:
        cv_pag = paginator.page(1)
    except EmptyPage:
        cv_pag = paginator.page(paginator.num_pages)

    context = {
        'interessados': cv_pag,
        'pages': paginator.page_range,
        'actual_page': page,
        'n_pages': int(paginator.num_pages),
        "user":request.user
    }

    return render(request, "cvs.html", context)

@has_curriculumdb_plan
def curriculo(request, pk):
    usuario = request.user
    template_name = "cv.html"
    context = {
        "interessado": Profile.objects.get(usuario=request.user)
    }
    return render(request, "cv.html", context)
