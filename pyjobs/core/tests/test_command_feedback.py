from unittest.mock import patch
from pyjobs.core.models import Skill
from django.test import TestCase
from six import StringIO
from pyjobs.core.models import Job
from pyjobs.marketing.models import Messages
from datetime import datetime, timedelta
from pyjobs.core.management.commands.load_skills import *
from django.core.management import call_command
from model_mommy import mommy
import sys


class FeedbackRequestTest(TestCase):
    def setUp(self):
        self.out = StringIO()
        sys.stdout = self.out
        self.job = mommy.make(
            Job, created_at=datetime.now() - timedelta(14), premium=True
        )
        mommy.make(Messages, message_type="feedback")
        self.job.premium_at = datetime.now() - timedelta(14)
        self.job.save()
        call_command("send_feedback_request", stdout=self.out)

    def test_output(self):
        self.assertEqual("True\n", self.out.getvalue())
