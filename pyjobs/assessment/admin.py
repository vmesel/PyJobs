from django.contrib import admin
from pyjobs.assessment.models import *


class AssessmentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("name", "theme", "creator", "language", "description")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "assessment", "correct_answer")


class PunctuationAdmin(admin.ModelAdmin):
    list_display = ("user", "question")


admin.site.register(AssessmentCategory, AssessmentCategoryAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Punctuation, PunctuationAdmin)
