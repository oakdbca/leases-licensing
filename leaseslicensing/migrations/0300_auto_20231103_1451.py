# Generated by Django 3.2.21 on 2023-11-03 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0299_proposal_added_internally'),
    ]

    operations = [
        migrations.RenameField(
            model_name='approval',
            old_name='original_leaselicense_number',
            new_name='original_leaselicence_number',
        ),
        migrations.RenameField(
            model_name='proposal',
            old_name='original_leaselicense_number',
            new_name='original_leaselicence_number',
        ),
    ]