# Generated by Django 5.1.7 on 2025-03-26 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0003_alter_equipment_is_calibrated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calibration',
            name='certificate',
            field=models.FileField(blank=True, upload_to='equipment/calibrations/', verbose_name='Uverenje o etaloniranju'),
        ),
        migrations.AlterField(
            model_name='internalcontrol',
            name='control_note',
            field=models.FileField(blank=True, upload_to='equipment/internal_controls/', verbose_name='Zapis o IK'),
        ),
    ]
