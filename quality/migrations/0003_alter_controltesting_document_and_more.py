# Generated by Django 5.1.7 on 2025-03-26 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controltesting',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='quality/control_testing/', verbose_name='Dokument'),
        ),
        migrations.AlterField(
            model_name='measurementuncertainty',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='quality/measurement_uncertainty/', verbose_name='Dokument'),
        ),
        migrations.AlterField(
            model_name='ptscheme',
            name='final_report',
            field=models.FileField(blank=True, null=True, upload_to='quality/pt_schemes/', verbose_name='Završni izveštaj'),
        ),
    ]
