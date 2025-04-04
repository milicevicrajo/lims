# Generated by Django 5.1.7 on 2025-03-24 09:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_alter_customuser_role'),
        ('methods', '0001_initial'),
        ('quality', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='controltestingmethod',
            name='staff',
            field=models.ManyToManyField(to='staff.staff', verbose_name='Osoblje'),
        ),
        migrations.AddField(
            model_name='measurementuncertainty',
            name='method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='methods.method', verbose_name='Metoda'),
        ),
        migrations.AddField(
            model_name='ptscheme',
            name='laboratory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.laboratory', verbose_name='Laboratorija'),
        ),
        migrations.AddField(
            model_name='ptschememethod',
            name='method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='methods.method', verbose_name='Metoda'),
        ),
        migrations.AddField(
            model_name='ptschememethod',
            name='pt_scheme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quality.ptscheme', verbose_name='Šema PT'),
        ),
        migrations.AddField(
            model_name='ptschememethod',
            name='staff',
            field=models.ManyToManyField(to='staff.staff', verbose_name='Osoblje'),
        ),
    ]
