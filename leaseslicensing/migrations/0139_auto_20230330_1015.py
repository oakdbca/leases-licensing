# Generated by Django 3.2.18 on 2023-03-30 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0138_merge_20230328_1018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approval',
            options={'verbose_name': 'Lease/License'},
        ),
        migrations.AddField(
            model_name='approvaluseraction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
        migrations.AddField(
            model_name='competitiveprocessuseraction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
        migrations.AddField(
            model_name='complianceuseraction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
        migrations.AddField(
            model_name='organisationaction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
        migrations.AddField(
            model_name='organisationrequestuseraction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
        migrations.AddField(
            model_name='proposaluseraction',
            name='who_full_name',
            field=models.CharField(default='Anonymous User', max_length=200),
        ),
    ]
