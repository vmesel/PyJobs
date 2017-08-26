from django.forms import ModelForm
from freela.models import Freela, Freelancer


class FreelaForm(ModelForm):
    class Meta:
        model = Freela
        fields = ["empresa", "email_responsavel_empresa", "link_da_empresa", "titulo_do_job", "descricao", "requisitos", "tipo_freela"]



class FreelancerForm(ModelForm):
    class Meta:
        model = Freelancer
        fields = ["nome", "email", "portfolio"]
