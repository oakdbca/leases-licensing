# Generated by Django 3.2.18 on 2023-08-04 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0234_auto_20230803_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvaltype',
            name='type',
            field=models.CharField(choices=[('lease', 'Lease'), ('licence', 'Licence')], max_length=10, null=True),
        ),
    ]