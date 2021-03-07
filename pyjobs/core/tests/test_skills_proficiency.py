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
            user = self.user,
            skill=self.skill[0],
            experience=2
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
            user = self.user,
            skill=self.skill[0],
            experience=2
        )
        response = self.client.get(reverse("user_proficiency"), follow=True)
        self.assertContains(response, skill_proficiency.skill.name)
    
    def test_if_fields_are_being_correctly_parsed(self):
        skill_proficiency = SkillProficiency.objects.create(
            user = self.user,
            skill=self.skill[0],
            experience=2
        )
        skill_proficiency_2 = SkillProficiency.objects.create(
            user = self.user,
            skill=self.skill[1],
            experience=2
        )

        form = SkillProficiencyForm(
            user=self.user,
            data = {
                "skill_0": skill_proficiency.pk,
                "skill_years_0": skill_proficiency.pk,
                "skill_1": skill_proficiency_2.pk,
                "skill_years_1": skill_proficiency_2.pk,
            }
        )
        form.is_valid()
        # import ipdb; ipdb.set_trace()
        assert form.cleaned_data == {
            "proficiency": [
                {
                    "skill": skill_proficiency.skill.pk,
                    "experience": skill_proficiency.experience,
                    "user": skill_proficiency.user,
                },
                {
                    "skill": skill_proficiency_2.skill.pk,
                    "experience": skill_proficiency_2.experience,
                    "user": skill_proficiency_2.user,
                }
            ]
        }

    def test_if_form_save_is_working_correctly(self):
        form = SkillProficiencyForm(
            user = self.user,
            data = {
                'skill_0': 1,
                'skill_years_0': 2,
            }
        )
        form.is_valid()
        form.save()
        assert SkillProficiency.objects.filter(user=self.user, skill__pk=1, experience=2).count() == 1