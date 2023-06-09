
import logging

from django.db import migrations
from django.core.management import call_command

logger = logging.getLogger(__name__)


fixtures_path = 'leaseslicensing/components/tenure/fixtures/'


def load_groups(apps, schema_editor):
    call_command('loaddata', fixtures_path + 'groups.json', verbosity=0)


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0184_approval_record_management_number'),
    ]

    operations = [
        migrations.RunPython(load_groups, atomic=True),
    ]
