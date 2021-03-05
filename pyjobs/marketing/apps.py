from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MarketingConfig(AppConfig):
    name = "marketing"
    verbose_name = _("Central de Marketing")

    def ready(self):
        import pyjobs.marketing.triggers