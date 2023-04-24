import json
import logging

from django.db import migrations
from django.core.management import call_command


logger = logging.getLogger(__name__)


fixtures_path = 'leaseslicensing/components/tenure/fixtures/'


def load_regions(apps, schema_editor):
    call_command('loaddata', fixtures_path + 'regions.json', verbosity=0)


def load_districts(apps, schema_editor):
    call_command('loaddata', fixtures_path + 'districts.json', verbosity=0)


def load_lgas(apps, schema_editor):
    call_command('loaddata', fixtures_path + 'lgas.json', verbosity=0)


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0149_category'),
    ]

    operations = [
        migrations.RunPython(load_regions, atomic=True),
        migrations.RunPython(load_districts, atomic=True),
        migrations.RunPython(load_lgas, atomic=True)
    ]
