from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "pyjobs.core"

    def ready(self):
        import pyjobs.core.triggers
