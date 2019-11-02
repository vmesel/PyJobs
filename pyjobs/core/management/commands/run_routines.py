import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("send_test_reminder")
        call_command("send_weekly_mailing")
        call_command("send_weekly_summary")
        return u"True"
