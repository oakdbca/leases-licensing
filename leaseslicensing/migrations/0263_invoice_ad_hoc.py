# Generated by Django 3.2.18 on 2023-09-07 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0262_auto_20230907_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='ad_hoc',
            field=models.BooleanField(default=False),
        ),
    ]