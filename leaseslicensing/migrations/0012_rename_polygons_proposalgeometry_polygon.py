# Generated by Django 3.2.4 on 2022-01-19 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("leaseslicensing", "0011_auto_20220119_1535"),
    ]

    operations = [
        migrations.RenameField(
            model_name="proposalgeometry",
            old_name="polygons",
            new_name="polygon",
        ),
    ]
