import os
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from core.models import Skills

class Command(BaseCommand):
    def _get_skills(self):
        skills = []
        raw_skills = open("_skills.txt")
        lines = [line for line in raw_skills.readlines()]
        raw_skills.close()
        for line in lines:
            skills.append(line)
        return skills

    def handle(self, *args, **options):
        qs_skills = Skills.objects.all()
        skills = self._get_skills()
        for skill in skills:
            try:
                skill_obj = Skills.objects.create(name=skill.strip())
            except IntegrityError as e:
                print(
                    "Skill '{}' already exists in the database".format(
                        skill
                    )
                )
