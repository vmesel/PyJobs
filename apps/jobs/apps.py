from django.apps import AppConfig

from watson import search as watson


class JobsAppConfig(AppConfig):
    name = 'apps.jobs'

    def ready(self):
        Job = self.get_model('Job')
        watson.register(Job)
