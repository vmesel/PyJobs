import os
from datetime import datetime

from django.core.management.base import BaseCommand
from pyjobs.core.management.commands.send_weekly_mailing import (
    Command as weekly_mailing,
)
from pyjobs.core.management.commands.send_weekly_summary import (
    Command as weekly_summary,
)
from pyjobs.core.management.commands.send_test_reminder import Command as test_reminder


class Command(BaseCommand):
    def handle(self, *args, **options):
        weekly_mailing.handle()
        weekly_summary.handle()
        test_reminder.handle()
