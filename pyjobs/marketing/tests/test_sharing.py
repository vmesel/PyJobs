from django.test import TestCase
from unittest.mock import patch
from model_mommy.mommy import make

from pyjobs.marketing.models import Contact, Messages
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from pyjobs.marketing.models import Share
from pyjobs.marketing.forms import SharingForm
from pyjobs.core.models import Job
from django.test import Client


class SharingModelTest(TestCase):
    @patch("pyjobs.marketing.triggers.post_telegram_channel")
    def setUp(self, _mocked_post_telegram_channel):
        self.user = User.objects.create_user(
            username="jacob",
            first_name="jacob",
            last_name="bocaj",
            email="jacob@gmail.com",
            password="top_secret",
            is_staff=True,
        )

        self.job = make(Job)

        self.sharing_obj = Share.objects.create(
            user_sharing=self.user, user_receiving_email="test@test.com", job=self.job
        )
        self.client = Client()

    def test_model_object_exists(self):
        qs = Share.objects.all()
        self.assertIn(self.sharing_obj, qs)

    def test_sharing_object_has_same_data_as_defined(self):
        obj = Share.objects.all().first()
        self.assertEqual(obj.user_sharing, self.user)
        self.assertEqual(obj.user_receiving_email, "test@test.com")
        self.assertEqual(obj.job, self.job)

    def test_form_instance_with_no_data(self):
        form = SharingForm({})
        self.assertFalse(form.is_valid())

    def test_form_instance_with_valid_data(self):
        form = SharingForm({"user_receiving_email": "test@test.com"})
        self.assertTrue(form.is_valid())

    def test_form_saving_with_valid_data(self):
        form = SharingForm(data={"user_receiving_email": "test2@test.com"})

        form.save(user_sharing=self.user, job=self.job)
        self.assertEqual(len(Share.objects.all()), 2)
        self.assertEqual(Share.objects.all()[1].user_receiving_email, "test2@test.com")
        self.assertEqual(Share.objects.all()[1].user_sharing, self.user)
        self.assertEqual(Share.objects.all()[1].job, self.job)

    def test_job_sharing_view_status_code(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/job/{}/share/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)

    def test_job_sharing_view_with_invalid_form_data(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/job/{}/share/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)
        data = {"user_receiving_email": "testing"}
        response_post = self.client.post(
            "/job/{}/share/".format(self.job.pk), data=data
        )
        content = response_post.content.decode("utf-8")
        self.assertEqual(response_post.status_code, 200)
        self.assertIn("Email inválido!", content)

    def test_job_sharing_view_with_valid_form_data(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get("/job/{}/share/".format(self.job.pk))
        self.assertEqual(response.status_code, 200)
        data = {"user_receiving_email": "testing@test.com"}
        response_post = self.client.post(
            "/job/{}/share/".format(self.job.pk), data=data
        )
        content = response_post.content.decode("utf-8")
        self.assertEqual(response_post.status_code, 200)
        self.assertIn("Email enviado ao Pythonista", content)
