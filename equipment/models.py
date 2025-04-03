from django.db import models
from core.models import Laboratory
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from django.conf import settings
import os


class Equipment(models.Model):
    EQUIPMENT_TYPE_CHOICES = [
        ('Glavna', 'Glavna'),
        ('Pomocna', 'Pomocna'),
    ]

    EQUIPMENT_GROUP_CHOICES = [
        ('Termometri', 'Termometri'),
        ('Komparateri', 'Komparateri'),
        ('Vage', 'Vage'),
        ('Manometri', 'Manometri'),
        ('Transdjuseri', 'Transdjuseri'),
        ('Aparati', 'Aparati'),
        ('Merni prsten', 'Merni prsten'),
        ('Ostalo', 'Ostalo'),
    ]

    card_number = models.CharField(_("Broj kartona"), max_length=255)
    name = models.CharField(_("Naziv opreme"), max_length=255)
    scope = models.CharField(_("Opseg/Tačnost"), max_length=255)
    manufacturer = models.CharField(_("Proizvođač"), max_length=255)
    type = models.CharField(_("Tip"), max_length=255)
    model = models.CharField(_("Model"), max_length=255)
    serial_number = models.CharField(_("Serijski broj"), max_length=255)
    inventory_number = models.CharField(_("Inventarski broj"), max_length=255)
    purchase_date = models.DateField(_("Datum nabavke"))
    usage_start_date = models.DateField(_("Datum stavljanja u upotrebu"))
    laboratory = models.ManyToManyField(Laboratory, related_name='equipment', verbose_name=_("Laboratorija"))
    responsible_laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='related_equipment', verbose_name=_("Odgovorna laboratorija"))
    location = models.CharField(_("Lokacija opreme"), max_length=255)
    other = models.TextField(_("Ostale bitne karakteristike"), max_length=255)
    equipment_type = models.CharField(_("Glavna/Pomoćna"), max_length=7, choices=EQUIPMENT_TYPE_CHOICES, default='Glavna')
    is_calibrated = models.BooleanField(_("Da li se kalibriše"), choices=[(True, "Da"), (False, "Ne")], default=True)

    # POMOCNA OPREMA
    main_equipment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_equipments', verbose_name=_("Glavna oprema"))
    group = models.CharField(_("Grupa"), max_length=20, choices=EQUIPMENT_GROUP_CHOICES, null=True, blank=True)

    # New field for tracking if the equipment is out of use (rashodovana)
    is_rashodovana = models.BooleanField(_("Rashodovana"), default=False, editable=False)
    last_modified = models.DateTimeField(auto_now=True)
    
    def get_absolute_url(self):
        return reverse('equipment_detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        if self.equipment_type == 'Glavna':
            self.main_equipment = None
        super(Equipment, self).save(*args, **kwargs)

    def __str__(self):
        return self.card_number

class Calibration(models.Model):

    FREQUENCY_OF_USE_CHOICES = [
        ('Nekoliko puta mesecno', 'Nekoliko puta mesecno'),
        ('Nekoliko puta nedeljno', 'Nekoliko puta nedeljno'),
        ('Svakodnevno', 'Svakodnevno'),
    ]
    CONDITIONS_OF_USE_CHOICES = [
        ('Kontrolisani lab. uslovi', 'Kontrolisani lab. uslovi'),
        ('Nekontrolisani lab. uslovi', 'Nekontrolisani lab. uslovi'),
        ('Korišćenje van lab.', 'Korišćenje van lab.'),
    ]
    ACCURACY_REQUIRED_CHOICES = [
        ('Nema zahtevanih propisa', 'Nema zahtevanih propisa'),
        ('Standardni nivo tačnosti', 'Standardni nivo tačnosti'),
        ('Visok nivo tačnosti', 'Visok nivo tačnosti'),
    ]
    UNCERTAINTY_TRACKING_CHOICES = [
        ('Opadanje MN', 'Opadanje MN'),
        ('Konstantna MN', 'Konstantna MN'),
        ('Rast MN', 'Rast MN'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    calibration_date = models.DateField(null=True, blank=True, verbose_name=_("Datum etaloniranja"))
    certificate_number = models.CharField(_("Broj uverenja o etaloniranju"), max_length=255, unique=True)
    calibration_laboratory = models.CharField(_("Laboratorija za etaloniranje"), max_length=255, blank=True)
    calibration_range = models.CharField(_("Opseg etaloniranja"), max_length=255, blank=True)
    measurement_uncertainty = models.CharField(_("Merna nesigurnost"), max_length=255, blank=True)
    certificate = models.FileField(_("Uverenje o etaloniranju"), upload_to='equipment/calibrations/', blank=True)
    
    # Automatski preracunati iz PROGRAMA ETALONIRANJA
    calibration_interval = models.CharField(_("Interval etaloniranja"), editable=False, max_length=255, null=True, blank=True)
    next_calibration_date = models.DateField(_("Datum ponovnog etaloniranja"), editable=False, null=True, blank=True)
    
    # Za potrebe intervala etaloniranja - PROGRAM ETALONIRANJA 
    equipment_age = models.FloatField(_("Starost opreme"), editable=False, null=True, blank=True)  # Automatically calculated, not stored in db
    frequency_of_use = models.CharField(_("Učestalost korišćenja opreme"), max_length=30, choices=FREQUENCY_OF_USE_CHOICES)
    conditions_of_use = models.CharField(_("Uslovi korišćenja i čuvanja"), max_length=30, choices=CONDITIONS_OF_USE_CHOICES)
    measurement_uncertainty_tracking = models.CharField(_("Praćenje merne nesigurnosti"), max_length=30, choices=UNCERTAINTY_TRACKING_CHOICES)
    required_accuracy = models.CharField(_("Zahtevana tačnost merenja"), max_length=30, choices=ACCURACY_REQUIRED_CHOICES)
    recommended_calibration_interval = models.PositiveIntegerField(_("Preporučeni interval etaloniranja"), validators=[MinValueValidator(1)]) 
    mandatory_calibration_interval = models.PositiveIntegerField(_("Produženi period etaloniranja"), null=True, blank=True) 

    pie_document_link = models.CharField(_("PIE veza sa dokumentom"), max_length=100, blank=True)
    calibration_note = models.TextField(_("Napomena o etaloniranju"), max_length=500, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def calculate_calibration_interval(self):

        if self.equipment_age < 1:
            ocena1 = 3
        elif self.equipment_age > 5:
            ocena1 = 1
        else:
            ocena1 = 2
        
        if self.frequency_of_use == 'Nekoliko puta mesecno':
            ocena2 = 3
        elif self.frequency_of_use == 'Nekoliko puta nedeljno':
            ocena2 = 2
        else: 
            ocena2 = 1

        if self.conditions_of_use == 'Kontrolisani lab. uslovi':
            ocena3 = 3
        elif self.conditions_of_use == 'Nekontrolisani lab. uslovi':
            ocena3 = 2
        else: 
            ocena3 = 1
        
        if self.measurement_uncertainty_tracking == 'Opadanje MN':
            ocena4 = 3
        elif self.measurement_uncertainty_tracking == 'Konstantna MN':
            ocena4 = 2
        else: 
            ocena4 = 1

        if self.required_accuracy == 'Nema zahtevanih propisa':
            ocena5 = 3
        elif self.required_accuracy == 'Standardni nivo tačnosti':
            ocena5 = 2
        else: 
            ocena5 = 1

        calculated_calibration_interval = int(ocena1*0.2 + ocena2*0.2 + ocena3*0.1 + ocena4*0.3 + ocena5*0.2)

        if self.mandatory_calibration_interval:
            selected_calibration_interval = self.mandatory_calibration_interval

        elif calculated_calibration_interval > self.recommended_calibration_interval:
            selected_calibration_interval = self.recommended_calibration_interval

        else:
            selected_calibration_interval = calculated_calibration_interval

        if self.calibration_date and isinstance(selected_calibration_interval, int):
            # Add the interval (in years) to the calibration_date to find the next_calibration_date
            self.next_calibration_date = self.calibration_date + relativedelta(years=selected_calibration_interval)

        return selected_calibration_interval, calculated_calibration_interval, ocena1, ocena2, ocena3, ocena4, ocena5
    
    def calculate_equipment_age(self):
        if not self.calibration_date or not self.equipment.purchase_date:
            return None
        delta = self.calibration_date - self.equipment.purchase_date
        age_in_years = delta.days / 365.25  # Account for leap years
        return round(age_in_years, 2)  # Rounding to two decimal places

    
    def save(self, *args, **kwargs):
        # Starost opreme u trenutku kalibracije
        self.equipment_age = self.calculate_equipment_age()
        # interval kalibracije
        self.calibration_interval, _, _, _, _, _, _ = self.calculate_calibration_interval()
        # datum naredne kalibracije
        self.next_calibration_date = self.calibration_date + relativedelta(years=self.calibration_interval)

        super(Calibration, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the certificate file if it exists
        if self.certificate:
            certificate_path = os.path.join(settings.MEDIA_ROOT, self.certificate.name)
            if os.path.isfile(certificate_path):
                os.remove(certificate_path)
        # Call the superclass method to delete the database record
        super().delete(*args, **kwargs)

class InternalControl(models.Model):
    name = models.CharField(_("Naziv interne kontrole"), max_length=100)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    last_control_date = models.DateField(_("Datum poslednjeg IK"))
    control_interval = models.IntegerField(_("Interval IK (meseci)"), help_text=_("Interval u mesecima"), validators=[MinValueValidator(1)])
    next_control_date = models.DateField(_("Datum ponovnog IK"), null=True, blank=True, editable=False)
    control_note = models.FileField(_("Zapis o IK"), upload_to='equipment/internal_controls/', blank=True)
    controlling_devices = models.ManyToManyField(Equipment, related_name='controlling_internal_controls', blank=True)
    note = models.TextField(_("NAPOMENA"), max_length=500, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate next_control_date based on last_control_date and control_interval
        if self.last_control_date and self.control_interval:
            self.next_control_date = self.last_control_date + relativedelta(months=self.control_interval)
        
        super(InternalControl, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Internal Control for {self.equipment.name}"

class Repair(models.Model):
    REPAIR_CHOICES = [
        ('Istitut IMS', 'Istitut IMS'),
        ('Spoljni servis', 'Spoljni servis'),
    ]
        
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    malfunction_date = models.DateField(_("Datum konstatovanja neispravnosti"))
    action_taken = models.TextField(_("Radnja pri kojoj je neispravnost utvrđena"))
    malfunction_description = models.TextField(_("Opis neispravnosti"))
    resolved_within_institute = models.CharField(_("Neispravnost otklonjena u"), max_length=20, choices=REPAIR_CHOICES, default='Istitut IMS')
    notes = models.TextField(_("Napomena"), null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Malfunction on {self.malfunction_date} for {self.equipment.name}"