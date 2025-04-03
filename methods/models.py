from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Laboratory

class Standard(models.Model):
    STANDARD_STATUS_CHOICES= [
        ('Aktivan', 'Aktivan'),
        ('Povučen', 'Povučen'),
    ]

    name = models.CharField(_("Naziv"), max_length=255)
    test_subject = models.ForeignKey('TestSubject', on_delete=models.SET_NULL, verbose_name=_("Predmet ispitivanja"), blank=True, null=True)
    reference_document_name = models.CharField(_("Naziv referentnog dokumenta"), max_length=255)
    designation = models.CharField(_("Oznaka"), max_length=255)
    year = models.IntegerField(_("Godina"))
    status = models.CharField(_("Status"), max_length=10, choices=STANDARD_STATUS_CHOICES)
    document = models.FileField(_("Dokument"), upload_to='methods/standards/', blank=True, null=True)

    def __str__(self):
        return f"{self.designation} - {self.name}"

class TestingArea(models.Model):
    area = models.CharField(_("Naziv oblasti ispitivanja"), max_length=255)
    code = models.CharField(_("Kod"), max_length=10)

    def __str__(self):
        return f"{self.area} - {self.code}"

class TestSubject(models.Model):
    subject = models.CharField(_("Naziv predmeta ispitivanja"), max_length=255)
    code = models.CharField(_("Kod"), max_length=10)

    def __str__(self):
        return f"{self.subject} - {self.code}"

class SubDiscipline(models.Model):
    name = models.CharField(_("Naziv poddiscipline"), max_length=255)
    testing_area = models.ForeignKey('TestingArea', on_delete=models.SET_NULL, verbose_name=_("Oblast ispitivanja"), blank=True, null=True)
    test_subject = models.ManyToManyField('TestSubject', verbose_name=_("Predmeti ispitivanja"), blank=True)
    description = models.TextField(_("Opis poddiscipline"), max_length=255)
    laboratory =  models.ForeignKey('core.Laboratory', on_delete=models.SET_NULL, verbose_name=_("Laboratorja"), blank=True, null=True)
    frequency_of_participation = models.IntegerField(_("Frekvencija učešća"))


    def __str__(self):
        return self.name

class Method(models.Model):
    LABORATORY_CHOICES = [
        ('Laboratorija', 'Laboratorija'),
        ('Teren', 'Teren'),
        ('Laboratorija i Teren', 'Laboratorija i Teren'),
        ('Uzorkovanje', 'Uzorkovanje'),
        ('Računska metoda', 'Računska metoda'),
    ]

    STATUS_CHOICES = [
        ('Akreditovana', 'Akreditovana'),
        ('Proširenje obima akreditacije', 'Proširenje obima akreditacije'),
        ('Van obima akreditacije', 'Van obima akreditacije'),
    ]

    name = models.CharField(_("Naziv metode"), max_length=255)
    testing_area = models.ForeignKey('TestingArea', on_delete=models.SET_NULL, verbose_name=_("Oblast ispitivanja"), blank=True, null=True)
    measurement_techniques = models.CharField(_("Merne tehnike"), max_length=255)
    property = models.CharField(_("Svojstvo"), max_length=255)
    test_subjects = models.ForeignKey('TestSubject', on_delete=models.SET_NULL, verbose_name=_("Predmet ispitivanja"), blank=True, null=True, related_name='primary_standard')
    standard = models.ForeignKey('Standard', on_delete=models.SET_NULL, verbose_name=_("Standard"),null=True, blank=True)
    standard_point = models.CharField(_("Tačka standarda"), null=True, blank=True, max_length=255)
    standard_secondary = models.ManyToManyField('Standard', verbose_name=_("Standard - dodatni"), related_name='secondary_standard')
    equipment = models.ManyToManyField('equipment.Equipment', verbose_name=_("Oprema"))
    subdiscipline = models.ForeignKey('SubDiscipline', on_delete=models.SET_NULL, verbose_name=_("Poddisciplina"),null=True, blank=True)
    laboratory = models.ForeignKey('core.Laboratory', on_delete=models.CASCADE, verbose_name=_("Laboratorija"))
    subject_and_area = models.CharField(_("Predmet i područje primene"), max_length=255, null=True, blank=True)
    samples = models.TextField(_("Uzorci"), null=True, blank=True)
    environmental_conditions = models.TextField(_("Uslovi sredine"), null=True, blank=True)
    testing_place = models.CharField(_("Mesto ispitivanja"), max_length=50, choices=LABORATORY_CHOICES, default='Laboratorija')
    method_status = models.CharField(_("Status metode"), max_length=50, choices=STATUS_CHOICES, default='Van obima akreditacije')
    description = models.TextField(_("Opis"))

    def __str__(self):
        if self.standard:
            return f"{self.standard.designation} - {self.name}"
        else:
            return self.name