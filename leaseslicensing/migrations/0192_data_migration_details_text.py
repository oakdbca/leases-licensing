import logging

from django.db import migrations
from django.core.management import call_command


logger = logging.getLogger(__name__)


fixtures_path = 'leaseslicensing/components/texts/fixtures/'


def load_details_text(apps, schema_editor):
    call_command('loaddata', fixtures_path + 'details_text.json', verbosity=0)


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0191_auto_20230619_0922'),
    ]

    operations = [
        migrations.RunPython(load_details_text, atomic=True),
    ]
