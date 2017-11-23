import django_filters

from .models import Job
from .utils import clean_money


class JobFilter(django_filters.FilterSet):
    salario = django_filters.CharFilter(
        method='filter_salario',
        label='Salário',
    )

    def filter_salario(self, queryset, name, value):
        value = float(clean_money(value))
        where = {
            '%s_minimo__lte' % name: value,
            '%s_maximo__gte' % name: value,
        }
        return queryset.filter(**where)

    class Meta:
        model = Job
        fields = {
            'titulo_do_job': ['icontains'],
            'home_office': ['exact'],
            'tipo_freela': ['exact'],
            'local': ['icontains'],
            'salario': [],
        }
