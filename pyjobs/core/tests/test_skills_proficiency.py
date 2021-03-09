from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
from model_bakery import baker as mommy
from model_bakery.recipe import Recipe

from pyjobs.core.models import Profile, Skill, SkillProficiency
from pyjobs.core.forms import SkillProficiencyForm


class SkillProficiencyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@gmail.com", password="top_secret"
        )
        self.client = Client()
        self.skill = mommy.make(Skill, _quantity=3, _fill_optional=True)
        self.profile = mommy.make(Profile, user=self.user, _fill_optional=True)

    def test_if_user_has_no_proficiency_registered(self):
        assert SkillProficiency.objects.filter(user=self.user).count() == 0

    def test_if_skill_proficiency_is_associated_with_user(self):
        skill_proficiency = SkillProficiency.objects.create(
            user=self.user, skill=self.skill[0], experience=2
        )
        assert SkillProficiency.objects.filter(user=self.user).count() == 1
        assert skill_proficiency.user == self.user
        assert skill_proficiency.skill == self.skill[0]
        assert skill_proficiency.user.profile == self.profile
        assert skill_proficiency.experience == 2

    def test_accessing_proficiency_page_without_auth(self):
        response = self.client.get(reverse("user_proficiency"), follow=True)
        assert len(response.redirect_chain) > 0

    def test_accessing_proficiency_page_with_auth(self):
        self.client.login(username=self.user.username, password="top_secret")
        response = self.client.get(reverse("user_proficiency"), follow=True)
        assert len(response.redirect_chain) == 0

    def test_accessing_proficiency_page_with_auth_and_existing_skill_proficiency(self):
        self.client.login(username=self.user.username, password="top_secret")
        skill_proficiency = SkillProficiency.objects.create(
            user=self.user, skill=self.skill[0], experience=2
        )
        response = self.client.get(reverse("user_proficiency"), follow=True)
        self.assertContains(response, skill_proficiency.skill.name)
