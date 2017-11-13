from apps.jobs.models import Job
import django_filters

class JobFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = ['titulo_do_job', 'home_office', 'tipo_freela', 'local' ]
