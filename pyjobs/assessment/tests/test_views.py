from django.test import TestCase, Client
from model_bakery import baker as mommy

from pyjobs.assessment.models import *
from django.contrib.auth.models import User
from django.urls import reverse

from random import getrandbits


class TestAssessmentViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@gmail.com", password="top_secret"
        )
        self.assessment = mommy.make(
            Assessment,
            public=True,
        )
        self.assessment.slug = "slug-test"
        self.assessment.save()

        self.questions = mommy.make(
            Question, assessment=self.assessment, _quantity=6, _fill_optional=True
        )
        self.client = Client()
        self.client.login(username="jacob", password="top_secret")

    def test_if_assessment_page_exists(self):
        response = self.client.get(reverse("quiz_home", args=[self.assessment.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Começar o Quiz", response.content.decode("utf-8"))

    def test_if_assessment_home_page_has_correct_text(self):
        self.right_punctuation = mommy.make(
            Punctuation,
            user=self.user,
            question=self.questions[0],
            correct_answer=True,
        )
        self.wrong_punctuation = mommy.make(
            Punctuation,
            user=self.user,
            correct_answer=False,
            question=self.questions[1],
        )
        response = self.client.get(reverse("quiz_home", args=[self.assessment.slug]))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Continuar Respondendo", content)

    def test_if_assessment_home_page_has_result_button(self):
        for question in self.questions:
            self.right_punctuation = mommy.make(
                Punctuation,
                user=self.user,
                question=question,
                correct_answer=bool(getrandbits(1)),
            )

        response = self.client.get(
            reverse("quiz_home", args=[self.assessment.slug]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ver resultado", response.content.decode("utf-8"))
        response = self.client.get(
            reverse("question_page", args=[self.assessment.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sua pontuação foi de", response.content.decode("utf-8"))
