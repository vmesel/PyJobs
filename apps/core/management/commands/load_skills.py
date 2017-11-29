import os
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from apps.core.models import Skills


class Command(BaseCommand):
    # TODO: Testar essa classe
    @staticmethod
    def _get_skills():
        base = os.path.dirname(os.path.abspath('__file__'))
        full_path = "{}/apps/core/management/commands/_skills.txt".format(base)
        skills = []
        raw_skills = open(full_path)
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
                skill_obj = Skills.objects.create(skill=skill.strip())
            except IntegrityError as e:
                print(
                    "Skill '{}' already exists in the database".format(
                        skill
                    )
                )
