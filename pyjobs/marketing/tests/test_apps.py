from django.apps import apps
from django.test import TestCase
from pyjobs.marketing.apps import MarketingConfig


class CoreConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(MarketingConfig.name, "pyjobs.marketing")
        self.assertEqual(apps.get_app_config("marketing").name, "pyjobs.marketing")
