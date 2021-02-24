import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from pyjobs.profiler.models import ProfilerData

from django.db import IntegrityError

from linkedin_scraper import Person, actions

from pprint import pprint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from time import sleep


def driver_factory():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    actions.login(driver, settings.LINKEDIN_EMAIL, settings.LINKEDIN_PASSWORD)
    return driver


class Command(BaseCommand):
    def handle(self, *args, **options):
        driver = driver_factory()

        for user in tqdm(
            User.objects.filter(profile__linkedin__isnull=False).exclude(
                profile__linkedin__in=["", " ", "\n"]
            )
        ):
            user_data = {
                "name": "",
                "about": "",
                "experiences": [],
                "education": [],
                "interests": [],
            }
            try:
                person = Person(
                    user.profile.linkedin,
                    contacts=[],
                    driver=driver,
                    close_on_complete=False,
                )
                user_data["name"] = person.name
                user_data["about"] = person.about

                for experience in person.experiences:
                    user_data["experiences"].append(
                        {
                            "description": experience.description,
                            "position_title": experience.position_title.replace(
                                "Nome da empresa\n", ""
                            ),
                            "duration": experience.duration,
                        }
                    )

                for education in person.educations:
                    user_data["educations"].append(
                        {
                            "from_date": education.from_date,
                            "to_date": education.to_date,
                            "degree": education.degree,
                            "company": education.company,
                        }
                    )

                user_data["interests"] = [
                    interest.title for interest in person.interests
                ]

                ProfilerData.objects.get_or_create(user=user, linkedin_data=user_data)
            except Exception as e:
                pass

        driver.close()
