from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from apps.core.models import Skills, Profile, Company

skills = Skills.objects.all()


class CadastreSeForm(UserCreationForm):
    telefone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ex: 11998445522'}), required=True)
    github = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': 'Preencha com o link do seu GitHub (não obrigatório)'}),
        required=False)
    linkedin = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': 'Preencha com o link do seu Linkedin (não obrigatório)'}),
        required=False)
    portfolio = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': 'Preencha com o link do seu portfolio (não obrigatório)'}),
        required=False)

    skills = forms.ModelMultipleChoiceField(
        label="Skills",
        queryset=skills,
        help_text="Selecione as skills que você tem",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(CadastreSeForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


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
