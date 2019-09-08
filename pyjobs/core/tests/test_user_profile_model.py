from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
import responses
from pyjobs.core.models import Profile


class ProfileTest(TestCase):
    @responses.activate
    def setUp(self):
        responses.add(
            responses.POST,
            "https://api.mailerlite.com/api/v2/subscribers",
            json={"status": "Success"},
            status=200,
        )

        self.user = User.objects.create_user(
            username="v@m.com",
            email="v@m.com",
            password="top_secret",
            first_name="Vinicius",
            last_name="Mesel",
        )
        self.profile = Profile(
            user=self.user,
            github="http://www.aaa.com.br",
            linkedin="http://www.aaa.com.br",
            portfolio="http://www.aaa.com.br",
        )
        self.profile.save()

    def test_create_profile_with_user(self):
        nome_real = "{} {}".format(self.user.first_name, self.user.last_name)
        self.assertTrue(str(self.profile), nome_real)

    def test_created(self):
        self.assertTrue(Profile.objects.exists())

    def test_created_at(self):
        self.assertIsInstance(self.profile.created_at, datetime)
