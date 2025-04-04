# Generated by Django 5.1.7 on 2025-03-24 09:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_alter_customuser_role'),
        ('equipment', '0003_alter_equipment_is_calibrated'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestingArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=255, verbose_name='Naziv oblasti ispitivanja')),
                ('code', models.CharField(max_length=10, verbose_name='Kod')),
            ],
        ),
        migrations.CreateModel(
            name='TestSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255, verbose_name='Naziv predmeta ispitivanja')),
                ('code', models.CharField(max_length=10, verbose_name='Kod')),
            ],
        ),
        migrations.CreateModel(
            name='SubDiscipline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Naziv poddiscipline')),
                ('description', models.TextField(max_length=255, verbose_name='Opis poddiscipline')),
                ('frequency_of_participation', models.IntegerField(verbose_name='Frekvencija učešća')),
                ('laboratory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.laboratory', verbose_name='Laboratorja')),
                ('testing_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='methods.testingarea', verbose_name='Oblast ispitivanja')),
                ('test_subject', models.ManyToManyField(blank=True, to='methods.testsubject', verbose_name='Predmeti ispitivanja')),
            ],
        ),
        migrations.CreateModel(
            name='Standard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Naziv')),
                ('reference_document_name', models.CharField(max_length=255, verbose_name='Naziv referentnog dokumenta')),
                ('designation', models.CharField(max_length=255, verbose_name='Oznaka')),
                ('year', models.IntegerField(verbose_name='Godina')),
                ('status', models.CharField(choices=[('Aktivan', 'Aktivan'), ('Povučen', 'Povučen')], max_length=10, verbose_name='Status')),
                ('document', models.FileField(blank=True, null=True, upload_to='standards/', verbose_name='Dokument')),
                ('test_subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='methods.testsubject', verbose_name='Predmet ispitivanja')),
            ],
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Naziv metode')),
                ('measurement_techniques', models.CharField(max_length=255, verbose_name='Merne tehnike')),
                ('property', models.CharField(max_length=255, verbose_name='Svojstvo')),
                ('standard_point', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tačka standarda')),
                ('subject_and_area', models.CharField(blank=True, max_length=255, null=True, verbose_name='Predmet i područje primene')),
                ('samples', models.TextField(blank=True, null=True, verbose_name='Uzorci')),
                ('environmental_conditions', models.TextField(blank=True, null=True, verbose_name='Uslovi sredine')),
                ('testing_place', models.CharField(choices=[('Laboratorija', 'Laboratorija'), ('Teren', 'Teren'), ('Laboratorija i Teren', 'Laboratorija i Teren'), ('Uzorkovanje', 'Uzorkovanje'), ('Računska metoda', 'Računska metoda')], default='Laboratorija', max_length=50, verbose_name='Mesto ispitivanja')),
                ('method_status', models.CharField(choices=[('Akreditovana', 'Akreditovana'), ('Proširenje obima akreditacije', 'Proširenje obima akreditacije'), ('Van obima akreditacije', 'Van obima akreditacije')], default='Van obima akreditacije', max_length=50, verbose_name='Status metode')),
                ('description', models.TextField(verbose_name='Opis')),
                ('equipment', models.ManyToManyField(to='equipment.equipment', verbose_name='Oprema')),
                ('laboratory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.laboratory', verbose_name='Laboratorija')),
                ('standard', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='methods.standard', verbose_name='Standard')),
                ('standard_secondary', models.ManyToManyField(related_name='secondary_standard', to='methods.standard', verbose_name='Standard - dodatni')),
                ('subdiscipline', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='methods.subdiscipline', verbose_name='Poddisciplina')),
                ('testing_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='methods.testingarea', verbose_name='Oblast ispitivanja')),
                ('test_subjects', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_standard', to='methods.testsubject', verbose_name='Predmet ispitivanja')),
            ],
        ),
    ]
