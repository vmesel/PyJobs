from pyjobs.core.models import Job, STATE_CHOICES, SALARY_RANGES, JOB_LEVELS
import django_filters


class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Título da Vaga"
    )
    requirements = django_filters.CharFilter(
        field_name="requirements", lookup_expr="icontains", label="Requisitos"
    )
    state = django_filters.ChoiceFilter(choices=STATE_CHOICES[:-1])
    salary_range = django_filters.ChoiceFilter(choices=SALARY_RANGES[:-1])
    job_level = django_filters.ChoiceFilter(choices=JOB_LEVELS[:-1])
    remote = django_filters.BooleanFilter(field_name="remote", label="Remoto?")
