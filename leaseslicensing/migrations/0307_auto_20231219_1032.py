# Generated by Django 3.2.23 on 2023-12-19 02:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0306_delete_globalsettings'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MapColumn',
        ),
        migrations.DeleteModel(
            name='MapLayer',
        ),
    ]
