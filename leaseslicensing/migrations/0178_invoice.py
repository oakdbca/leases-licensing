# Generated by Django 3.2.18 on 2023-05-24 08:36

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import leaseslicensing.components.invoicing.models
import leaseslicensing.components.main.models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0177_auto_20230524_1540'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lodgement_number', models.CharField(blank=True, max_length=9, null=True)),
                ('status', models.CharField(blank=True, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('void', 'Void')], max_length=40, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('inc_gst', models.BooleanField(default=True)),
                ('date_issued', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_due', models.DateField(null=True)),
                ('invoice_pdf', leaseslicensing.components.main.models.SecureFileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/protected_media', location='/home/oak/dev/leases-licensing/protected_media'), upload_to=leaseslicensing.components.invoicing.models.invoice_pdf_upload_path)),
                ('approval', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='leaseslicensing.approval')),
            ],
            options={
                'ordering': ['-date_issued', 'approval'],
            },
        ),
    ]