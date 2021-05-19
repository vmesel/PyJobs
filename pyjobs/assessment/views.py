from django.shortcuts import get_object_or_404, render, redirect, reverse, HttpResponse
from django.utils.translation import gettext_lazy as _
from pyjobs.assessment.models import *
from django.contrib.auth.decorators import login_required
from pyjobs.core.utils import generate_thumbnail_quiz

from random import shuffle


def quiz_home(request, unique_slug):
    assessment = get_object_or_404(Assessment, slug=unique_slug)
    if request.user.is_authenticated:
        started_answering, finished = Punctuation.objects.unanswered_questions(
            request.user, assessment
        )
    else:
        started_answering, finished = None, None

    quiz_ranking = Punctuation.objects.ranking(assessment)

    return render(
        request,
        "quiz_index.html",
        context={
            "assessment": assessment,
            "finished": finished,
            "started_answering": started_answering,
            "quiz_ranking": quiz_ranking,
        },
    )


@login_required
def question_page(request, unique_slug):
    assessment = get_object_or_404(Assessment, slug=unique_slug)
    question = Question.objects.filter(assessment=assessment).exclude(
        punctuation__in=Punctuation.objects.filter(user=request.user)
    )

    if question.count() == 0:
        return render(
            request,
            "quiz_final_page.html",
            context={
                "assessment": assessment,
                "punctuation": Punctuation.objects.assessment_grade(
                    request.user, assessment
                )
                * 100,
            },
        )

    question = question.order_by("?").first()

    possible_answers = [
        question.correct_answer,
        question.first_incorrect_answer,
        question.second_incorrect_answer,
        question.third_incorrect_answer,
        question.forth_incorrect_answer,
    ]
    shuffle(possible_answers)

    return render(
        request,
        "quiz_question.html",
        context={
            "assessment": assessment,
            "question": question,
            "possible_answers": possible_answers,
        },
    )


@login_required
def question_submit(request, unique_slug, question_id):
    if request.method != "POST":
        return redirect("/")

    question = get_object_or_404(Question, pk=question_id)
    Punctuation.objects.create(
        question=question,
        user=request.user,
        correct_answer=request.POST.get("answer") == question.correct_answer,
    )

    return redirect(reverse("question_page", args=[unique_slug]))


def quiz_thumbnail(request, unique_slug):
    quiz = Assessment.objects.filter(slug=unique_slug).first()
    im = generate_thumbnail_quiz(quiz=quiz)

    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")
    return response
