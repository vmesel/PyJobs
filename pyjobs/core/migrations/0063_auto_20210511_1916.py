# Generated by Django 3.2.2 on 2021-05-11 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0062_auto_20210330_1421"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="country",
            name="core_countr_name_c51781_idx",
        ),
        migrations.AlterUniqueTogether(
            name="skillproficiency",
            unique_together=set(),
        ),
    ]