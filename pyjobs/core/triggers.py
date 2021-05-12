from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from github import Github

from webpush import send_group_notification
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from pyjobs.core.models import Profile

from social_django.models import UserSocialAuth


@receiver(post_save, sender=UserSocialAuth)
def new_user_created_via_social_network(sender, instance, created, **kwargs):
    if not created and Profile.objects.filter(user=instance.user).count() > 0:
        return

    Profile.objects.create(user=instance.user)
