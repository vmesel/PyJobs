import requests

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.forms import ModelForm
from datetime import datetime
from django_select2.forms import Select2MultipleWidget, Select2Widget

from pyjobs.core.models import Job, Profile, Skill, JobApplication, SkillProficiency
from pyjobs.marketing.models import Contact
from django.utils.translation import gettext_lazy as _


class CustomModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomModelForm, self).__init__(*args, **kwargs)

    def is_valid(self, g_recaptcha_response):
        if not settings.RECAPTCHA_SECRET_KEY:
            return super().is_valid()

        data = {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": g_recaptcha_response,
        }
        recaptcha_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify", data=data
        )

        result = recaptcha_response.json()

        return ("success" in result) and super().is_valid()


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


class RegisterForm(UserCreationForm):
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


class SkillProficiencyForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.data = kwargs.get("data") if kwargs.get("data") is not None else {}

        for key in self.data:
            if "skill" in key and "years" not in key: 
                self.fields[key] = forms.CharField(
                    widget = forms.Select(
                        choices = [(skill.pk, skill.name) for skill in Skill.objects.all()]
                    ),
                    initial = self.data[key]
                )
            else:
                self.fields[key] = forms.IntegerField(
                    initial = self.data[key]
                )

        self.order_skills()
        self.is_bound = self.data is not None or files is not None
    
    def order_skills(self):
        self.skills = set()
        self.skills_proficiency = []
        self.skill_proficiency = [item for item in self.fields if "skill_" in item and "_years_" not in item]
        self.skill_proficiency.sort()
        self.years_proficiency = [item for item in self.fields if "skill_years_" in item]
        self.years_proficiency.sort()

        self.skill_years = zip(self.skill_proficiency, self.years_proficiency)
        
    def clean(self):
        for i, proficiency in enumerate(self.skill_years, start=0):
            skill, years = proficiency
            if skill in self.skills:
                self.add_error(f"skill_{i}", "Duplicate")
            else:
                self.skills_proficiency.append({
                    "skill": self.cleaned_data[skill],
                    "experience": self.cleaned_data[years],
                    "user": self.user
                })
        self.cleaned_data = {}
        self.cleaned_data["proficiency"] = self.skills_proficiency

    def save(self, commit=True):
        if not commit:
            return
        
        for skill_proficiency in self.cleaned_data["proficiency"]:
            SkillProficiency.objects.get_or_create({
                    "skill": Skill.objects.get(pk=skill_proficiency["skill"]),
                    "experience": skill_proficiency["experience"],
                    "user": self.user
            })


