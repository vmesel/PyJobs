from pyjobs.core.models import Skill
from django.test import TestCase
from six import StringIO
from pyjobs.core.management.commands.load_skills import *
from django.core.management import call_command
import sys


class LoadSkillTest(TestCase):
    def setUp(self):
        self.out = StringIO()
        sys.stdout = self.out
        call_command("load_skills", stdout=self.out)

    def test_output(self):
        self.assertEqual("True\n", self.out.getvalue())

    def test_len_default_skills(self):
        self.assertEqual(419, len(Skill.objects.all()))
