from django.test import TestCase
from model_mommy import mommy

from pyjobs.core.forms import *
from pyjobs.core.models import Skills


class RegisterFormTest(TestCase):
    def test_empty_form_is_not_valid(self):
        form = RegisterForm(data={})
        self.assertTrue(form.is_valid() == False)

    def test_form_is_valid(self):
        skills = mommy.make('core.Skills', _quantity=1, _fill_optional=True)
        form = RegisterForm(data={
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
            "skills_": skills
        })

        self.assertTrue(form.is_valid() == True)
