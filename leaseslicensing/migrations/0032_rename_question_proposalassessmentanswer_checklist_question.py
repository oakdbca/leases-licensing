# Generated by Django 3.2.4 on 2022-02-07 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0031_alter_proposalassessment_submitter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposalassessmentanswer',
            old_name='question',
            new_name='checklist_question',
        ),
    ]
