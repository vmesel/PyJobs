from django.conf.urls import url

from apps.curriculumdb.views import *

urlpatterns = [
    url(r'^$', lista_de_curriculos, name="lista_de_curriculos"),
    url(r'^cv/(?P<pk>\d+)/', curriculo, name="curriculo"),
    # url(r'^cadastro/', cadastrese, name="cadastro_view"),
]
