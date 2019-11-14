from django.test import TestCase
from model_mommy.mommy import make

from pyjobs.marketing.models import CustomerQuote
from django.test import Client

class QuotesModelTesting(TestCase):
    def setUp(self):
        self.quote = CustomerQuote(
            customer_name = "teste",
            company_name = "teste",
            avatar_name = "teste",
            customer_quote = "teste"
        )
        self.quote.save()

    def test_if_quote_is_registered(self):
        qs = CustomerQuote.objects.all()
        self.assertIn(self.quote, qs)

    def test_quote_attributes(self):
        qs = CustomerQuote.objects.all().first()
        self.assertEqual(self.quote.customer_name, qs.customer_name)
        self.assertEqual(self.quote.company_name, qs.company_name)
        self.assertEqual(self.quote.avatar_name, qs.avatar_name)
        self.assertEqual(self.quote.customer_quote, qs.customer_quote)

    def test_quote_values(self):
        qs = CustomerQuote.objects.all().first()
        self.assertEqual(qs.customer_name, "teste")
        self.assertEqual(qs.company_name, "teste")
        self.assertEqual(qs.avatar_name, "teste")
        self.assertEqual(qs.customer_quote, "teste")
