from django.forms import ModelForm
from apps.jobs.models import Job, Person


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ["empresa", "email_responsavel_empresa", "link_da_empresa", "titulo_do_job", "local", "descricao", "requisitos", "tipo_freela"]



class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ["nome", "email", "portfolio"]
