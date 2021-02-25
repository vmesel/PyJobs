import os
import re
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from django.db import IntegrityError

from github import Github, GithubException

from tqdm import tqdm

g = Github(settings.GITHUB_ACCESS_TOKEN)


class Command(BaseCommand):
    def handle(self, *args, **options):

        for user in tqdm(User.objects.exclude(profile__github__isnull=True)):
            user_data = {
                "github": {
                    "repos": {},
                    "followers": {},
                }
            }
            username_search = re.search(
                ".com/(.*)(\/|\?)?\/(.*)", user.profile.github, re.IGNORECASE
            )
            if username_search:
                username = username_search.group(1)
            else:
                continue

            try:
                github_user = g.get_user(username)
            except GithubException:
                continue

            for repo in list(github_user.get_repos()):
                user_data["github"]["repos"][repo.name] = {
                    "forks": repo.forks_count,
                    "stars": len(list(repo.get_stargazers())),
                    "subscribers": len(list(repo.get_subscribers())),
                    "tags_quantity": len(list(repo.get_tags())),
                    "topics": list(repo.get_topics()),
                    "language": repo.language,
                    "issues": repo.open_issues_count,
                    "watchers": repo.watchers_count,
                }

            user.profiledata.github_data = user_data
            user.profiledata.save()
