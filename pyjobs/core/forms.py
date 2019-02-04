from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms

from django_select2.forms import Select2Widget, Select2MultipleWidget

from pyjobs.core.models import Job, Contact, Profile


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'workplace', 'company_name', 'application_link',
            'company_email', 'description', 'requirements', 'skills',
            'ad_interested'
        ]
        widgets = {
            'skills': Select2MultipleWidget
        }

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.widget.attrs.update({'placeholder': field.label})

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ["name","subject","email","message"]


class RegisterForm(UserCreationForm):
    github = forms.URLField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Preencha com o link do seu GitHub (não obrigatório)'
            }
        ), required=False)

    linkedin = forms.URLField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Preencha com o link do seu Linkedin (não obrigatório)'
            }
        ), required=False)

    portfolio = forms.URLField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Preencha com o link do seu portfolio (não obrigatório)'
            }
        ), required=False)

    cellphone = forms.CharField(label='Celular',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Preencha com o seu telefone'
            }
        ), required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('github', 'linkedin', 'portfolio', 'cellphone')
