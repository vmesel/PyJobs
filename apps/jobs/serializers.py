from apps.jobs.models import Freela
from rest_framework import serializers


class Freela(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Freela
        fields = ('empresa', 'email_responsavel_empresa', 'link_da_empresa', 'titulo_do_job', 'link_job', 'descricao', 'requisitos')
