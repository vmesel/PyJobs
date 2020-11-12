from pyjobs.core.models import Job, STATE_CHOICES, SALARY_RANGES, JOB_LEVELS, CONTRACT
import django_filters


class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Título da Vaga"
    )
    state = django_filters.ChoiceFilter(choices=STATE_CHOICES[:-1])
    contract_form = django_filters.ChoiceFilter(choices=CONTRACT)
    remote = django_filters.BooleanFilter(field_name="remote", label="Remoto?")
    salary_range = django_filters.ChoiceFilter(choices=SALARY_RANGES[:-1])
    job_level = django_filters.ChoiceFilter(choices=JOB_LEVELS[:-1])
