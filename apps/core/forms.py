from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from apps.core.models import Skills, Profile, Company

skills = Skills.objects.all()

class CadastreSeForm(UserCreationForm):
    telefone = forms.CharField(help_text="Formato: (11) 99999-9999")
    github = forms.URLField(help_text="Informe o link do seu Github, caso você tenha um")
    linkedin = forms.URLField(help_text="Informe o link do seu Linkedin, caso você tenha um")
    portfolio = forms.URLField(help_text="Informe o link do seu Portfolio, caso você tenha um", required=False)
    skills = forms.ModelMultipleChoiceField(
        label="Skills",
        queryset=skills,
        help_text="Selecione a quantidade de skills "
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('telefone', 'github', 'linkedin', 'portfolio', 'interesse_banco_cv', 'skills',)

class EditCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("nome", "email", "site", "descricao")
