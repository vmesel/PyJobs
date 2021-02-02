from datetime import timedelta, datetime
from hashlib import sha512

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


from pyjobs.settings import (
    SECRET_KEY,
    STATE_CHOICES,
    SALARY_RANGES,
    JOB_LEVELS,
    CONTRACT,
    FEEDBACK_TYPE,
)
from pyjobs.core.managers import PublicQuerySet, ProfilingQuerySet
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    name = models.CharField(_("Nome da Moeda"), max_length=300, blank=False, help_text=_("Ex.: Euro"))
    slug = models.CharField(_("Abreviação"), max_length=300, blank=False, help_text=_("Ex.: EUR"))

    def __str__(self):
        return self.slug


class Country(models.Model):
    name = models.CharField(_("Nome do País"), max_length=300, blank=False, help_text=_("Ex.: Brasil"))

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.URLField(verbose_name=_("GitHub"), blank=True, default="")
    linkedin = models.URLField(verbose_name=_("LinkedIn"), blank=True, default="")
    portfolio = models.URLField(verbose_name=_("Portfolio"), blank=True, default="")
    cellphone = models.CharField(
        verbose_name=_("Telefone"),
        max_length=16,
        validators=[
            RegexValidator(
                regex="^((?:\([1-9]{2}\)|\([1-9]{2}\) |[1-9]{2}|[1-9]{2} )(?:[2-8]|9[1-9])[0-9]{3}(?:\-[0-9]{4}| [0-9]{4}|[0-9]{4}))$",
                message=_(
                    "Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen."
                ),
            )
        ],
    )
    state = models.IntegerField("Seu Estado", choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        _("Sua Faixa Salarial Atual"), choices=SALARY_RANGES, default=6
    )
    job_level = models.IntegerField("Seu nível atual", choices=JOB_LEVELS, default=5)
    bio = models.TextField(
        _("Sua Bio"),
        default="",
        help_text=_(
            "Descreva um pouco sobre você para as empresas poderem te conhecer melhor!"
        ),
    )
    on_mailing_list = models.BooleanField("Está na mailing list", default=False)
    agree_privacy_policy = models.BooleanField(
        _("Aceitou políticas de privacidade"), default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skill")

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __repr__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfis")
        ordering = ["-created_at"]

    objects = models.Manager.from_queryset(ProfilingQuerySet)()

    def profile_skill_grade(self, job):
        skills = self.skills.values_list("pk", flat=True)
        job_skills = Job.objects.get(pk=job).skills.values_list("pk", flat=True)
        return Profile.objects.grade(skills, job_skills)


class JobError(Exception):
    pass


class Job(models.Model):
    title = models.CharField(
        _("Título da Vaga"),
        max_length=10000,
        default="",
        blank=False,
        help_text=_("Ex.: Desenvolvedor"),
    )
    workplace = models.CharField(
        _("Local"),
        max_length=10000,
        default="",
        blank=False,
        help_text=_("Ex.: Santana - São Paulo"),
    )
    company_name = models.CharField(
        _("Nome da Empresa"),
        max_length=10000,
        default="",
        blank=False,
        help_text=_("Ex.: ACME Inc"),
    )
    application_link = models.URLField(
        verbose_name=_("Link para a Vaga"),
        blank=True,
        default="",
        help_text=_("Ex.: http://goo.gl/hahaha"),
    )
    company_email = models.EmailField(
        verbose_name=_("Email da Empresa"), blank=False, help_text=_("Ex.: abc@def.com")
    )
    description = models.TextField(
        _("Descrição da vaga"),
        default="",
        help_text=_("Descreva um pouco da sua empresa e da vaga, tente ser breve"),
    )
    requirements = models.TextField(
        _("Requisitos da vaga"),
        default="",
        help_text=_(
            "Descreva os requisitos da sua empresa em bullet points\n\n-Usar Git\n-Saber Java"
        ),
    )
    premium = models.BooleanField("Premium?", default=False)
    public = models.BooleanField("Público?", default=True)
    receive_emails = models.BooleanField("Enviar emails?", default=True)
    ad_interested = models.BooleanField("Impulsionar*", default=False)
    challenge_interested = models.BooleanField("Desafio*", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    premium_at = models.DateTimeField(
        "Data de mudança de Status", blank=True, null=True
    )
    cellphone = models.CharField(
        verbose_name=_("WhatsApp para contato"),
        max_length=16,
        help_text=_("Deixe seu WhatsApp para contatarmos sobre nossos serviços"),
        null=True,
    )
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, default=1)
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, default=1)
    skills = models.ManyToManyField("Skill")
    is_open = models.BooleanField(_("Vaga aberta"), default=True)
    is_challenging = models.BooleanField(_("Enviar Chall"), default=False)
    challenge = models.TextField(_("Challenge"), blank=True, null=True)

    state = models.IntegerField(_("Estado"), choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        _("Faixa Salarial"), choices=SALARY_RANGES, default=1
    )
    job_level = models.IntegerField(
        _("Nível do Profissional"), choices=JOB_LEVELS, default=1
    )
    contract_form = models.IntegerField(
        _("Forma de contratação"), choices=CONTRACT, default=1
    )
    remote = models.BooleanField(_("Esta vaga é remota?"), default=False)
    consultancy = models.BooleanField(_("Consultoria?"), default=False)
    issue_number = models.IntegerField(_("Issue do Github"), null=True, blank=True)

    objects = models.Manager.from_queryset(PublicQuerySet)()

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.title} - {self.company_name} - {self.pk}"

    def get_application_link(self):
        return self.application_link if self.application_link != "" else False

    def get_premium_jobs(term=None):
        return Job.objects.premium().created_in_the_last(30).search(term)

    def get_index_display_jobs():
        return Job.objects.public().created_in_the_last(30)[:9]

    def get_publicly_available_jobs(term=None):
        return Job.objects.not_premium().created_in_the_last(30).search(term)

    def get_feed_jobs():
        return Job.objects.not_premium().created_in_the_last(7)

    def get_excerpt(self):
        return self.description[:500]

    def applied(self, request_user):
        return JobApplication.objects.filter(job=self, user=request_user).exists()

    def apply(self, request_user):
        JobApplication.objects.create(job=self, user=request_user)
        return True

    def get_weekly_summary(self):
        return Job.objects.created_in_the_last(7)

    def get_absolute_url(self):
        return "/job/{}".format(self.pk)

    def get_jobs_to_get_feedback(self):
        return Job.objects.created_in_the_last(15)

    def get_expiration_date(self):
        return self.created_at + timedelta(days=30)

    def close_hash(self, salt=None):
        if not all((self.pk, self.created_at)):
            raise JobError("Unsaved Job models have no close hash")

        salt = salt or SECRET_KEY
        value = "::".join(("close", salt, str(self.pk), str(self.created_at)))
        obj = sha512(value.encode("utf-8"))
        return obj.hexdigest()

    def listing_hash(self, salt=None):
        if not all((self.pk, self.created_at)):
            return "Unsaved Job models have no listing URL"

        salt = salt or SECRET_KEY
        value = "::".join(("listing", salt, str(self.pk), str(self.created_at)))
        obj = sha512(value.encode("utf-8"))
        return obj.hexdigest()

    def get_close_url(self):
        if not all((self.pk, self.created_at)):
            raise JobError("Unsaved Job models have no close URL")

        kwargs = {"pk": self.pk, "close_hash": self.close_hash()}
        return reverse("close_job", kwargs=kwargs)

    def get_listing_url(self):
        if not all((self.pk, self.created_at)):
            return "Unsaved Job models have no listing URL"

        return "/job/{}/details/?job_hash={}".format(self.pk, self.listing_hash())


class JobApplication(models.Model):
    user = models.ForeignKey(User, default="", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, default="", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    challenge_response_link = models.URLField(
        _("Link de resposta ao desafio"), default="", blank=True, null=True
    )
    challenge_response_at = models.DateTimeField(blank=True, null=True)
    challenge_resent = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    output_sent = models.BooleanField(default=False)
    company_feedback = models.CharField(blank=True, null=True, max_length=3000)
    company_feedback_type = models.IntegerField(
        _("Tipo de feedback"), choices=FEEDBACK_TYPE, default=5
    )

    class Meta:
        unique_together = ("user", "job")
        verbose_name = _("Job Application")
        verbose_name_plural = _("Job Applications")

    def __str__(self):
        return " ".join(map(str, [self.user, _("applied to"), self.job]))

    def feedback_type(self):
        return FEEDBACK_TYPE[self.company_feedback_type - 1][1]


class Skill(models.Model):
    name = models.CharField(_("Skill"), max_length=100, default="", blank=False)
    unique_slug = models.CharField(
        _("Slug Unica"), max_length=1000, blank=True, null=True
    )
    description = models.TextField(
        _("Descrição da skill"), default="", blank=True, null=True
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def generate_slug(self):
        self.unique_slug = slugify(self.name)
        self.save()
