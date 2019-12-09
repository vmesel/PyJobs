from django.test import TestCase
from ..models import Partner
from model_mommy import mommy
from model_mommy.recipe import Recipe


class TestPartnerModel(TestCase):
    def setUp(self):
        self.partner = Recipe(Partner).make()

    def test_if_model_exists(self):
        qs = Partner.objects.all()
        self.assertIn(self.partner, qs)
