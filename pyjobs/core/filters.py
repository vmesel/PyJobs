from pyjobs.core.models import Job, STATE_CHOICES, SALARY_RANGES, JOB_LEVELS, CONTRACT, Country
from django.utils.translation import gettext_lazy as _
import django_filters


class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label=_("Título da Vaga")
    )
    country = django_filters.ModelChoiceFilter(queryset=Country.objects.all(), label=_("País"))
    contract_form = django_filters.ChoiceFilter(choices=CONTRACT)
    remote = django_filters.BooleanFilter(field_name="remote", label=_("Remoto?"))
    salary_range = django_filters.ChoiceFilter(choices=SALARY_RANGES[:-1])
    job_level = django_filters.ChoiceFilter(choices=JOB_LEVELS[:-1])
