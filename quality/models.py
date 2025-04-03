from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Laboratory
from methods.models import Method
from django.dispatch import receiver

class PTScheme(models.Model):
    TYPE_CHOICES = [
        ('ILC', 'ILC'),
        ('PT', 'PT'),
        ('EQA', 'EQA'),
    ]
    
    laboratory = models.ForeignKey('core.Laboratory', on_delete=models.CASCADE, verbose_name=_("Laboratorija"))
    organizer = models.CharField(_("Organizator"), max_length=255)
    code_name = models.CharField(_("Naziv ILC, PT ili EQA"), max_length=10, choices=TYPE_CHOICES, default='PT')
    final_report = models.FileField(_("Završni izveštaj"), upload_to='quality/pt_schemes/', blank=True, null=True)
    final_report_number = models.CharField(_("Broj završnog izveštaja"), max_length=50)
    final_report_date = models.DateField(_("Datum završnog izveštaja"))
    year = models.IntegerField(_("Godina"))

    def __str__(self):
        return f"{self.code_name} - {self.year} - {self.laboratory}"


class PTSchemeMethod(models.Model):
    pt_scheme = models.ForeignKey(PTScheme, on_delete=models.CASCADE, verbose_name=_("Šema PT"))
    method = models.ForeignKey('methods.Method', on_delete=models.CASCADE, verbose_name=_("Metoda"))
    number_of_participants = models.IntegerField(_("Broj učesnika"))
    z_score = models.TextField(_("Z skor"), blank=True)
    staff = models.ManyToManyField('staff.Staff', verbose_name=_("Osoblje"))
    measures_taken = models.TextField(_("Preuzete mere"), blank=True)

    def __str__(self):
        return f"{self.pt_scheme} - {self.method}"


class ControlTesting(models.Model):    
    laboratory = models.ForeignKey('core.Laboratory', on_delete=models.CASCADE, verbose_name=_("Laboratorija"))
    report_number = models.CharField(_("Broj izveštaja"), max_length=255)
    report_date = models.DateField(_("Datum izveštaja"))
    document = models.FileField(_("Dokument"), upload_to='quality/control_testing/', blank=True, null=True)

    def __str__(self):
        return f"{self.report_number} - {self.report_date}"
    
class ControlTestingMethod(models.Model): 
    control_test = models.ForeignKey('ControlTesting', on_delete=models.CASCADE, verbose_name=_("Kontrolno ispitivanje"))
    method = models.ForeignKey('methods.Method', on_delete=models.CASCADE, verbose_name=_("Metoda"))
    number_of_participants = models.IntegerField(_("Broj učesnika"))
    staff = models.ManyToManyField('staff.Staff', verbose_name=_("Osoblje"))
    measures_taken = models.TextField(_("Preuzete mere"), blank=True)

    def __str__(self):
        return f"KI za Metodu - {self.method}"
       
class MeasurementUncertainty(models.Model):
    method = models.ForeignKey('methods.Method', on_delete=models.CASCADE, verbose_name=_("Metoda"))
    document_name = models.CharField(_("Naziv dokumenta"), max_length=255)
    uncertainty_value = models.CharField(_("Vrednost nesigurnosti"), max_length=50)
    calculation_date = models.DateField(_("Datum proračuna"))
    report_number = models.CharField(_("Broj izveštaja"), max_length=255)
    document = models.FileField(_("Dokument"), upload_to='quality/measurement_uncertainty/', blank=True, null=True)

    def __str__(self):
        return f"{self.report_number}"