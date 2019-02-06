from django.test import TestCase, override_settings
from unittest.mock import patch, PropertyMock

from django.contrib.auth.models import User
from pyjobs.core.models import Job, Profile

from pyjobs.core.newsletter import subscribe_user_to_chimp


class TestNewsletterSubscription(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='v@m.com',
            email="v@m.com",
            password="top_secret",
            first_name="Vinicius",
            last_name="Mesel"
        )
        self.profile = Profile(
            user = self.user,
            github = "http://www.aaa.com.br",
            linkedin = "http://www.aaa.com.br",
            portfolio = "http://www.aaa.com.br",
        )
        self.profile.save()

    @override_settings(MAILCHIMP_API_KEY=None,
        MAILCHIMP_USERNAME=None, MAILCHIMP_LIST_KEY=None)
    def test_subscribe_fails_if_no_api_key(self):
        response = subscribe_user_to_chimp(self.profile)
        self.assertFalse(response)

    @override_settings(MAILCHIMP_API_KEY="ABC",
        MAILCHIMP_USERNAME="ABC", MAILCHIMP_LIST_KEY="ABC")
    @patch('pyjobs.core.newsletter.MailChimp')
    def test_mailchimp_client_is_called_correctly(self, _mocked_mailchimp):
        response = subscribe_user_to_chimp(self.profile)
        _mocked_mailchimp.assert_called_once_with("ABC", "ABC")

        self.assertTrue(response)
