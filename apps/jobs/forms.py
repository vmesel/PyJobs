from django.forms import ModelForm
from apps.jobs.models import Job


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            "titulo_do_job",
            "home_office",
            "local",
            "descricao",
            "requisitos",
            "tipo_freela",
            "nivel"
        ]
