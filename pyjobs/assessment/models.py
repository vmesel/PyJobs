from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from pyjobs.assessment.managers import AssessmentQuerySet


class AssessmentCategory(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    description = models.TextField(max_length=5000, null=False, blank=False)
    slug = models.CharField(max_length=500, null=True, blank=True)

    def save(self, commit=True):
        if commit:
            self.slug = slugify(self.name)

        super(AssessmentCategory, self).save()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<AssessmentCategory(name={self.name})>"

    class Meta:
        verbose_name = _("Categoria do Teste")
        verbose_name_plural = _("Categorias dos Testes")


class Assessment(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    theme = models.ForeignKey(AssessmentCategory, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    time_limit = models.IntegerField(default=None, blank=True, null=True)
    language = models.CharField(max_length=500, choices=settings.LANGUAGES)
    slug = models.CharField(max_length=500, null=True, blank=True)
    public = models.BooleanField(default=True)
    description = models.TextField(max_length=5000, null=False, blank=False)
    auth_required = models.BooleanField(default=False)

    def save(self, commit=True):
        if commit:
            self.slug = slugify(self.name)

        super(Assessment, self).save()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Assessment(name={self.name})>"

    @property
    def question_count(self):
        return self.question_set.count()

    class Meta:
        verbose_name = _("Teste")
        verbose_name_plural = _("Testes")


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.CharField(max_length=5000, null=False, blank=False)
    correct_answer = models.CharField(max_length=5000, null=False, blank=False)
    first_incorrect_answer = models.CharField(max_length=5000, null=False, blank=False)
    second_incorrect_answer = models.CharField(max_length=5000, null=False, blank=False)
    third_incorrect_answer = models.CharField(max_length=5000, null=False, blank=False)
    forth_incorrect_answer = models.CharField(max_length=5000, null=False, blank=False)

    def __str__(self):
        return self.question

    def __repr__(self):
        return f"<AssessmentQuestion({self.id}, {self.assessment})>"

    class Meta:
        verbose_name = _("Pergunta")
        verbose_name_plural = _("Perguntas")


class Punctuation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct_answer = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(AssessmentQuerySet)()

    class Meta:
        unique_together = ("user", "question")
        verbose_name = _("Pontuação")
        verbose_name_plural = _("Pontuações")
