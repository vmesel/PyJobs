from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from model_mommy import mommy

from core.models import Job

class IndexViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('index')
        self.client = Client()
        self.publicly_jobs = mommy.make('core.Job', _quantity=10)

    def tearDown(self):
        Job.objects.all().delete()

    def test_view_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_context(self):
        response = self.client.get(self.url)
        self.assertFalse('index' in response.context)
        job_list = response.context['publicly_jobs']
        self.assertEquals(job_list.count(), 10)
        paginator = response.context['paginator']
        self.assertEquals(paginator.num_pages, 2)

    def test_page_not_found(self):
        response = self.client.get('{}?page=3'.format(self.url))
        self.assertEquals(response.status_code, 404) 