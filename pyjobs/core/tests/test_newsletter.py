from unittest.mock import patch, call

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from unittest.mock import patch
import responses
from pyjobs.core.models import Job, Profile
from pyjobs.core.newsletter import subscribe_user_to_chimp
from django.conf import settings


class NewsletterTest(TestCase):
    @responses.activate
    def setUp(self):
        responses.add(
            responses.POST,
            'https://api.mailerlite.com/api/v2/subscribers',
            json={'status': 'Success'},
            status=200
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

    def test_subscribe_to_newsletter(self):
        self.assertFalse(subscribe_user_to_chimp(self.profile))

    @override_settings(
        MAILCHIMP_API_KEY="AAA", MAILCHIMP_USERNAME="BBB", MAILCHIMP_LIST_KEY="CCC"
    )
    @patch("pyjobs.core.newsletter.MailChimp")
    def test_if_called(self, patched_mc):
        sub = subscribe_user_to_chimp(self.profile)
        patched_mc.assert_called_once_with("AAA", "BBB")
        patched_mc.return_value.lists.members.create.assert_called_once_with(
            "CCC", {"status": "subscribed", "email_address": "v@m.com"}
        )
