from django.shortcuts import render
from .models import Partner


def get_all_partners(request):
    context = {"partners": Partner.objects.all()}
    return render(request, template_name="partners.html", context=context)
