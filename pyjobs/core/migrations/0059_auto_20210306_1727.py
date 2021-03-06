# Generated by Django 3.1.7 on 2021-03-06 17:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0058_auto_20210223_2134"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="unique_slug",
            field=models.CharField(
                blank=True, max_length=1000, null=True, verbose_name="Slug Unica"
            ),
        ),
        migrations.CreateModel(
            name="SkillProficiency",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "experience",
                    models.IntegerField(default=0, verbose_name="Anos de experiência"),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        default="",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.skill",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default="",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
