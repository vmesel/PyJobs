from django.forms import ModelForm, CharField
from django.core.exceptions import ValidationError

from .models import Job
from .utils import clean_money


class JobForm(ModelForm):

    salario_minimo = CharField(max_length=30, required=False)
    salario_maximo = CharField(max_length=30, required=False)

    def clean_salario_minimo(self):
        return clean_money(self.cleaned_data.get('salario_minimo', 0))

    def clean_salario_maximo(self):
        return clean_money(self.cleaned_data.get('salario_maximo', 0))

    def clean(self):
        salario_minimo = self.cleaned_data.get('salario_minimo', 0)
        salario_maximo = self.cleaned_data.get('salario_maximo', 0)

        if salario_minimo > salario_maximo:
            raise ValidationError(
                'Salário mínimo não pode ser maior que o salário máximo.',
                code='invalid'
            )

    def save(self, commit=True):
        instance = super(JobForm, self).save(commit=False)

        salario_maximo = self.cleaned_data.get('salario_maximo', 0)
        salario_minimo = self.cleaned_data.get('salario_minimo', 0)

        instance.salario_minimo = salario_minimo
        instance.salario_maximo = salario_maximo

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Job
        fields = [
            "titulo_do_job",
            "home_office",
            "local",
            "descricao",
            "requisitos",
            "tipo_freela",
            "salario_minimo",
            "salario_maximo",
            "publico",
        ]
