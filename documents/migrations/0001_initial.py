# Generated by Django 5.1.7 on 2025-03-24 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(max_length=255, verbose_name='Naziv dokumenta')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Opis')),
                ('document_file', models.FileField(upload_to='documentation/', verbose_name='Dokument')),
                ('upload_date', models.DateField(auto_now_add=True, verbose_name='Datum učitavanja')),
            ],
        ),
        migrations.CreateModel(
            name='MethodDocumentation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(max_length=255, verbose_name='Naziv dokumenta')),
                ('document_file', models.FileField(upload_to='documentation/', verbose_name='Dokument')),
                ('upload_date', models.DateField(auto_now_add=True, verbose_name='Datum učitavanja')),
            ],
        ),
    ]
