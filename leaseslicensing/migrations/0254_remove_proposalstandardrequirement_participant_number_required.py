# Generated by Django 3.2.18 on 2023-08-25 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0253_auto_20230825_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposalstandardrequirement',
            name='participant_number_required',
        ),
    ]
