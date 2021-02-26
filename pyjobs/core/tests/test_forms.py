from django.test import TestCase
from model_mommy import mommy
from datetime import timedelta

from pyjobs.core.forms import *
from pyjobs.core.models import Skill, Profile, Job, Country, Currency
from unittest.mock import patch
from django.contrib.auth.models import User


class RegisterFormTest(TestCase):
    def test_empty_form_is_not_valid(self):
        form = RegisterForm(data={})
        self.assertTrue(form.is_valid() == False)

    def test_form_is_valid(self):
        skills = mommy.make("core.Skill", _quantity=1, _fill_optional=True)
        form = RegisterForm(
            data={
                "first_name": "Vinicius",
                "last_name": "Mesel",
                "email": "fakeemail@somewhere.com",
                "username": "foobar",
                "password1": "foopass123",
                "password2": "foopass123",
                "github": "http://www.google.com",
                "linkedin": "http://www.google.com",
                "portfolio": "http://www.google.com",
                "cellphone": "(11)987485552",
                "skills_": skills,
                "agree_privacy_policy": True,
            }
        )

        self.assertTrue(form.is_valid() == True)


class JobApplicationFormTest(TestCase):
    def test_empty_form_is_valid(self):
        form = JobApplicationForm(data={})
        self.assertTrue(form.is_valid())

    def test_filled_form_is_valid(self):
        form = JobApplicationForm(
            data={"challenge_response_link": "http://www.google.com"}
        )
        self.assertTrue(form.is_valid())


class JobApplicationFormWithContentTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.job = mommy.make(
            Job, _fill_optional=False, public=True, is_challenging=False
        )
        self.job.generate_slug()
        self.profile = mommy.make(Profile, _fill_optional=True)

        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.profile.user,
            email_sent_at=datetime.now() - timedelta(days=4),
            challenge_resent=False,
            challenge_response_at=None,
        )

    def test_form_saving(self):
        form = JobApplicationForm(instance=self.job_application)
        form.save()
        self.assertTrue(self.job_application.challenge_response_at is not None)


class RegisterFormTest(TestCase):
    def setUp(self):
        self.skills = mommy.make(Skill, _quantity=5)

    def test_invalid_form(self):
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())

    @patch("pyjobs.marketing.triggers.subscribe_user_to_mailer")
    def test_valid_form(self, _mocked_subscription):
        data = {
            "github": "http://www.google.com",
            "linkedin": "http://www.google.com",
            "portfolio": "http://www.google.com",
            "cellphone": "11981435390",
            "skills_": self.skills,
            "first_name": "Vvv",
            "last_name": "Mmm",
            "email": "v@m.com",
            "password1": "#T3st3123!",
            "username": "test_user",
            "on_mailing_list": True,
            "agree_privacy_policy": True,
        }
        data["password2"] = data["password1"]
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.user = User.objects.all().first()
        self.profile = Profile.objects.filter(user=self.user).first()
        self.assertTrue(self.profile.github == data["github"])
        self.assertTrue(_mocked_subscription.called)

    @patch("pyjobs.marketing.triggers.subscribe_user_to_mailer")
    def test_valid_form_but_without_mailer(self, _mocked_subscription):
        data = {
            "github": "http://www.google.com",
            "linkedin": "http://www.google.com",
            "portfolio": "http://www.google.com",
            "cellphone": "11981435390",
            "skills_": self.skills,
            "first_name": "Vvv",
            "last_name": "Mmm",
            "email": "v@m.com",
            "password1": "#T3st3123!",
            "username": "test_user",
            "on_mailing_list": False,
            "agree_privacy_policy": True,
        }
        data["password2"] = data["password1"]
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.user = User.objects.all().first()
        self.profile = Profile.objects.filter(user=self.user).first()
        self.assertTrue(self.profile.github == data["github"])
        self.assertFalse(_mocked_subscription.called)


class JobApplicationFeedbackFormTest(TestCase):
    @patch("pyjobs.marketing.triggers.send_group_notification")
    @patch("pyjobs.marketing.triggers.send_job_to_github_issues")
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(
        self, _mocked_send_group_push, _mock_github, _mocked_post_telegram_channel
    ):
        self.country = mommy.make(Country)
        self.currency = mommy.make(Currency)
        self.job = mommy.make(
            Job,
            public=True,
            country=self.country,
            currency=self.currency,
            is_challenging=False,
        )
        self.profile = mommy.make(Profile, _fill_optional=True)

        self.job_application = JobApplication.objects.create(
            job=self.job,
            user=self.profile.user,
            email_sent_at=datetime.now() - timedelta(days=4),
            challenge_resent=False,
            challenge_response_at=None,
        )

    def test_form_without_feedback(self):
        self.assertTrue(self.job_application.company_feedback is None)

    def test_saving_with_content(self):
        data = {
            "company_feedback": "Teste",
            "company_feedback_type": 1,
        }
        form = JobApplicationFeedbackForm(instance=self.job_application, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(
            self.job_application.company_feedback == data["company_feedback"]
        )
        self.assertTrue(
            self.job_application.company_feedback_type == data["company_feedback_type"]
        )


class EditProfileFormTest(TestCase):
    def setUp(self):
        self.profile = mommy.make(Profile, _fill_optional=True)
        self.skills = mommy.make("core.Skill", _quantity=1, _fill_optional=True)

    def test_email_change_on_form(self):
        data = {
            "email": "zezinho@huguinho.com",
            "cellphone": "11912345678",
            "skills": self.skills,
        }
        past_email = self.profile.user.email
        form = EditProfileForm(instance=self.profile, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        new_email = self.profile.user.email
        self.assertTrue(past_email != new_email)

    def test_form_is_empty_failing(self):
        form = EditProfileForm(instance=self.profile, data={})
        self.assertFalse(form.is_valid())
