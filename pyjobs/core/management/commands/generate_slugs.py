import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from pyjobs.core.models import Skill


class Command(BaseCommand):
    def handle(self, *args, **options):
        skills = Skill.objects.filter(unique_slug=None).all()

        for skill in skills:
            skill.generate_slug()

        return "True"
