# from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from freela.models import Freela
from rest_framework import viewsets
from freela.serializers import Freela as FreelaSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class ShowAvailableJobs(viewsets.ModelViewSet):
    queryset = Freela.objects.all()
    serializer_class = FreelaSerializer


# TODO: Criar endpoint na API para mostrar dados de um JOB especifico
