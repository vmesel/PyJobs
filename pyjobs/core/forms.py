import requests

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.forms import ModelForm, formset_factory, inlineformset_factory
from datetime import datetime
from django_select2.forms import Select2MultipleWidget, Select2Widget

from pyjobs.core.models import Job, Profile, Skill, JobApplication, SkillProficiency
from pyjobs.marketing.models import Contact
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorDict
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


class CustomModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomModelForm, self).__init__(*args, **kwargs)

    def is_valid(self, g_recaptcha_response):
        if settings.DEBUG and not settings.RECAPTCHA_SECRET_KEY:
            return super().is_valid()

        data = {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": g_recaptcha_response,
        }
        recaptcha_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify", data=data
        )

        result = recaptcha_response.json()

        return result["success"] and super().is_valid()


class JobForm(CustomModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "job_level",
            "company_name",
            "workplace",
            "remote",
            "state",
            "application_link",
            "company_email",
            "cellphone",
            "salary_range",
            "description",
            "requirements",
            "skills",
            "challenge_interested",
            "ad_interested",
            "contract_form",
            "currency",
            "country",
        ]
        widgets = {"skills": Select2MultipleWidget}

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})


class ContactForm(CustomModelForm):
    class Meta:
        model = Contact
        fields = ["name", "subject", "email", "message"]


class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ["challenge_response_link"]

    def save(self, commit=True):
        if commit:
            self.instance.challenge_response_at = datetime.now()
            self.instance.save()


class RegisterForm(CustomModelForm, UserCreationForm):

    error_messages = {
        'password_mismatch': _("Os campos de senha não coincidem."),
    }

    github = forms.URLField(
        label=_("Github (opcional)"),
        widget=forms.TextInput(attrs={"placeholder": _("Link do seu GitHub")}),
        required=False,
    )

    linkedin = forms.URLField(
        label=_("Linkedin (opcional)"),
        widget=forms.TextInput(attrs={"placeholder": _("Link do seu Linkedin")}),
        required=False,
    )

    portfolio = forms.URLField(
        label=_("Portfolio (opcional)"),
        widget=forms.TextInput(attrs={"placeholder": _("Link do seu portfolio")}),
        required=False,
    )

    cellphone = forms.CharField(
        label=_("Celular"),
        widget=forms.TextInput(attrs={"placeholder": _("Preencha com o seu telefone")}),
        required=True,
    )

    skills_ = forms.ModelMultipleChoiceField(
        label=_("Skills"), queryset=Skill.objects.all(), widget=Select2MultipleWidget
    )

    on_mailing_list = forms.BooleanField(
        label=_("Ao clicar, você aceita estar em nosso mailing list"), required=False
    )

    agree_privacy_policy = forms.BooleanField(
        label=_("Ao clicar, você aceita nossa política de privacidade"), required=True
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for fieldname in ["password1", "password2"]:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(commit=False)

        if commit:
            instance.save()

            profile = Profile(
                user=instance,
                github=self.cleaned_data["github"],
                linkedin=self.cleaned_data["linkedin"],
                portfolio=self.cleaned_data["portfolio"],
                cellphone=self.cleaned_data["cellphone"],
                on_mailing_list=self.cleaned_data["on_mailing_list"],
                agree_privacy_policy=self.cleaned_data["agree_privacy_policy"],
            )
            authenticate(
                username=instance.username, password=self.cleaned_data.get("password1")
            )
            profile.save()
            profile.skills.set(self.cleaned_data["skills_"])
            profile.save()
        return instance


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Seu e-mail"),
        widget=forms.TextInput(attrs={"placeholder": _("seu-email@atualizado.com")}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = ("github", "linkedin", "portfolio", "cellphone", "skills")
        widgets = {"skills": Select2MultipleWidget}

    def save(self, commit=True):
        if commit:
            user = self.instance.user
            user.email = self.cleaned_data["email"]
            user.profile.github = self.cleaned_data["github"]
            user.profile.linkedin = self.cleaned_data["linkedin"]
            user.profile.portfolio = self.cleaned_data["portfolio"]
            user.profile.cellphone = self.cleaned_data["cellphone"]
            user.profile.skills.set(self.cleaned_data["skills"])
            user.profile.save()
            user.save()

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields["email"].initial = self.instance.user.email


class JobApplicationFeedbackForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ["company_feedback", "company_feedback_type"]


class SkillProficiencyForm(ModelForm):
    class Meta:
        model = SkillProficiency
        fields = ["skill", "experience"]
