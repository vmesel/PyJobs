# Generated by Django 3.1.7 on 2021-03-30 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_auto_20210309_0954'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='country',
            index=models.Index(fields=['name'], name='core_countr_name_5737bb_idx'),
        ),
    ]
