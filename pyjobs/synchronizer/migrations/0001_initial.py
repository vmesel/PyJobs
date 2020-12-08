from django.apps import apps as global_apps
from django.db import migrations


def fix_first_site_name(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    first_site = Site.objects.get(pk=1)

    first_site.name = "PyJobs"
    first_site.domain = "pyjobs.com.br"
    first_site.save()


def adds_sites(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    sites_to_create = [{"name": "FrontJobs", "domain": "frontjobs.com.br"}]

    for site in sites_to_create:
        new_site = Site.objects.create(**site)
        new_site.save()


class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(fix_first_site_name),
        migrations.RunPython(adds_sites),
    ]

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]
