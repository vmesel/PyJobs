from django.test import TestCase, Client
from model_bakery import baker as mommy

from pyjobs.assessment.models import *
from django.urls import reverse
from django.contrib.auth.models import User


class TestAssessmentModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@gmail.com", password="top_secret"
        )
        self.assessment = mommy.make(
            Assessment,
            name="test",
            public=True,
        )

        self.questions = mommy.make(
            Question, assessment=self.assessment, _quantity=6, _fill_optional=True
        )
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
        self.client = Client()

    def test_if_assessment_exists(self):
        self.assertIn(self.assessment, Assessment.objects.all())

    def test_if_questions_exists(self):
        for question in self.questions:
            self.assertIn(question, Question.objects.all())

    def test_if_user_has_score(self):
        self.assertEqual(
            Punctuation.objects.assessment_grade(self.user, self.assessment), 0.5
        )

    def test_if_quiz_is_accessible_by_user(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(
            reverse("quiz_home", args=[self.assessment.slug]), follow=False
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.assessment.name, response.content.decode("utf-8"))
        self.assertIn(self.assessment.description, response.content.decode("utf-8"))
        self.assertIn(self.assessment.theme.name, response.content.decode("utf-8"))
