from datetime import timedelta, datetime
from hashlib import sha512

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


from pyjobs.settings import SECRET_KEY, STATE_CHOICES, SALARY_RANGES, JOB_LEVELS
from pyjobs.core.managers import PublicQuerySet, ProfilingQuerySet


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.URLField(verbose_name="GitHub", blank=True, default="")
    linkedin = models.URLField(verbose_name="LinkedIn", blank=True, default="")
    portfolio = models.URLField(verbose_name="Portfolio", blank=True, default="")
    cellphone = models.CharField(
        verbose_name="Telefone",
        max_length=16,
        validators=[
            RegexValidator(
                regex="^((?:\([1-9]{2}\)|\([1-9]{2}\) |[1-9]{2}|[1-9]{2} )(?:[2-8]|9[1-9])[0-9]{3}(?:\-[0-9]{4}| [0-9]{4}|[0-9]{4}))$",
                message="Telefone inválido! Digite entre 11 e 15 caracteres que podem conter números, espaços, parênteses e hífen.",
            )
        ],
    )
    state = models.IntegerField("Seu Estado", choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        "Sua Faixa Salarial Atual", choices=SALARY_RANGES, default=6
    )
    job_level = models.IntegerField("Seu nível atual", choices=JOB_LEVELS, default=5)
    bio = models.TextField(
        "Sua Bio",
        default="",
        help_text="Descreva um pouco sobre você para as empresas poderem te conhecer melhor!",
    )
    on_mailing_list = models.BooleanField("Está na mailing list", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("Skill")

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __repr__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
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
        "Título da Vaga",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: Desenvolvedor",
    )
    workplace = models.CharField(
        "Local",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: Santana - São Paulo",
    )
    company_name = models.CharField(
        "Nome da Empresa",
        max_length=100,
        default="",
        blank=False,
        help_text="Ex.: ACME Inc",
    )
    application_link = models.URLField(
        verbose_name="Link para a Vaga",
        blank=True,
        default="",
        help_text="Ex.: http://goo.gl/hahaha",
    )
    company_email = models.EmailField(
        verbose_name="Email da Empresa", blank=False, help_text="Ex.: abc@def.com"
    )
    description = models.TextField(
        "Descrição da vaga",
        default="",
        help_text="Descreva um pouco da sua empresa e da vaga, tente ser breve",
    )
    requirements = models.TextField(
        "Requisitos da vaga",
        default="",
        help_text="Descreva os requisitos da sua empresa em bullet points\n\n-Usar Git\n-Saber Java",
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
        verbose_name="WhatsApp para contato",
        max_length=16,
        help_text="Deixe seu WhatsApp para contatarmos sobre nossos serviços",
        null=True,
    )
    skills = models.ManyToManyField("Skill")
    is_open = models.BooleanField("Vaga aberta", default=True)
    is_challenging = models.BooleanField("Enviar Chall", default=False)
    challenge = models.TextField("Challenge", blank=True, null=True)

    state = models.IntegerField("Estado", choices=STATE_CHOICES, default=27)
    salary_range = models.IntegerField(
        "Faixa Salarial", choices=SALARY_RANGES, default=6
    )
    job_level = models.IntegerField(
        "Nível do Profissional", choices=JOB_LEVELS, default=5
    )
    remote = models.BooleanField("Esta vaga é remota?", default=False)

    objects = models.Manager.from_queryset(PublicQuerySet)()

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.title} - {self.company_name} - {self.pk}"

    def get_application_link(self):
        return self.application_link if self.application_link != "" else False

    def get_premium_jobs():
        return Job.objects.premium().created_in_the_last(30, premium=True)[:7]

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

    def get_close_url(self):
        if not all((self.pk, self.created_at)):
            raise JobError("Unsaved Job models have no close URL")

        kwargs = {"pk": self.pk, "close_hash": self.close_hash()}
        return reverse("close_job", kwargs=kwargs)


class JobApplication(models.Model):
    user = models.ForeignKey(User, default="", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, default="", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    challenge_response_link = models.URLField(
        "Link de resposta ao desafio", default="", blank=True, null=True
    )
    challenge_response_at = models.DateTimeField(blank=True, null=True)
    challenge_resent = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    output_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "job")
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

    def __str__(self):
        return "{} applied to {}".format(self.user, self.job)


class Skill(models.Model):
    name = models.CharField("Skill", max_length=100, default="", blank=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
