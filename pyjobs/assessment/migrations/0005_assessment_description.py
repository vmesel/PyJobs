# Generated by Django 3.1.7 on 2021-03-09 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0004_assessmentcategory_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="description",
            field=models.CharField(default="", max_length=5000),
            preserve_default=False,
        ),
    ]
