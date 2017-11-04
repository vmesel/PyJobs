from django.test import TestCase
from django.contrib.auth.models import User

from apps.jobs.models import Job, InterestedPerson

from model_mommy import mommy


class JobTestCase(TestCase):

    def setUp(self):
        self.job = mommy.make(Job, titulo_do_job='test')

    def test_job_creation(self):
        self.assertTrue(isinstance(self.job, Job))
        self.assertEqual(self.job.__str__(), self.job.titulo_do_job)


class InterestedPersonTestCase(TestCase):

    def setUp(self):
        self.job = mommy.make(Job, titulo_do_job='test')
        self.user = mommy.make(User, username='test', first_name='test', last_name='test')
        self.interested_person = mommy.make(InterestedPerson, job=self.job, usuario=self.user)

    def test_interested_person_creation(self):
        self.assertTrue(isinstance(self.interested_person, InterestedPerson))
        self.assertEqual(self.interested_person.__str__(),
                         'Relação de {} com {}'
                         .format(self.job, self.user.get_full_name()))
