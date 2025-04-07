from django import forms
from .models import *
from django_select2.forms import Select2Widget
from django.core.exceptions import ValidationError
from django_select2.forms import Select2MultipleWidget

class EquipmentForm(forms.ModelForm):
    laboratory = forms.ModelMultipleChoiceField(
        queryset=Laboratory.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Laboratorije u kojima se koristi"
    )

    purchase_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum nabavke"
    )

    usage_start_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum stavljanja u upotrebu"
    )

    main_equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(equipment_type="Glavna"),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Glavna oprema",
        required=False
    )

    class Meta:
        model = Equipment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ako user postoji, filtriraj podatke po korisniku
        if user:
            # Filtriraj izbor glavne opreme prema organizacionoj jedinici usera
            if hasattr(user, 'laboratory') and user.laboratory:
                org_unit = user.laboratory.organizational_unit
                self.fields['main_equipment'].queryset = Equipment.objects.filter(
                    equipment_type="Glavna",
                    responsible_laboratory__organizational_unit=org_unit
                )

            # Kontrola odgovorne laboratorije
            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                self.fields['responsible_laboratory'] = forms.ModelChoiceField(
                    queryset=Laboratory.objects.all(),
                    required=True,
                    label="Odgovorna laboratorija",
                    widget=Select2Widget(attrs={'class': 'select2-method'}),
                )
            else:
                # Automatski postavi laboratoriju za običnog korisnika
                self.fields['responsible_laboratory'] = forms.ModelChoiceField(
                    queryset=Laboratory.objects.filter(id=user.laboratory.id),
                    initial=user.laboratory.id,
                    label="Odgovorna laboratorija",
                    widget=forms.HiddenInput(),
                    required=False
                )
                self.instance.responsible_laboratory = user.laboratory

        # Formatiranje datuma kod prikaza forme
        if self.instance.pk:
            if self.instance.purchase_date:
                self.initial['purchase_date'] = self.instance.purchase_date.strftime('%Y-%m-%d')
            if self.instance.usage_start_date:
                self.initial['usage_start_date'] = self.instance.usage_start_date.strftime('%Y-%m-%d')

    # Clean metoda za dodatnu sigurnost ako treba da procesuiraš liste
    def clean_laboratory(self):
        return self.cleaned_data.get('laboratory', [])
    
    
class CalibrationForm(forms.ModelForm):
    calibration_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum etaloniranja"
    )
    class Meta:
        model = Calibration
        fields = '__all__'    

        labels = {
            'equipment': 'Oprema',
            'calibration_date': 'Datum etaloniranja',
            # Add more field labels as needed
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs and remove it
        super(CalibrationForm, self).__init__(*args, **kwargs)
        self.user = user  # Save the user for later use in the form
        if self.instance.id:  # Check if instance is being updated
            self.initial['calibration_date'] = self.instance.calibration_date.strftime('%Y-%m-%d')
        # Restrict the queryset for equipment if the user is not a superuser
        if not user.is_superuser:
            self.fields['equipment'].queryset = Equipment.objects.filter(responsible_laboratory__in=user.laboratory_permissions.all())


class InternalControlForm(forms.ModelForm):
    last_control_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum poslednje IK"
    )
    class Meta:
        model = InternalControl
        fields = '__all__'
        exclude = ['controlling_devices']  # Exclude controlling_devices field
        widgets = {
            'last_control_date': forms.DateInput(),
        } 

        labels = {
            'equipment': 'Karton opreme',
        }
    
    def __init__(self, *args, **kwargs):
        super(InternalControlForm, self).__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['last_control_date'] = self.instance.last_control_date.strftime('%Y-%m-%d')


class RepairForm(forms.ModelForm):
    malfunction_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum konstatovanja neispravnosti"
    )
    class Meta:
        model = Repair
        fields = '__all__'
        widgets = {
            'malfunction_date': forms.DateInput(),
        }

        labels = {
            'equipment': 'Karton opreme',
        }

    def __init__(self, *args, **kwargs):
        super(RepairForm, self).__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['malfunction_date'] = self.instance.malfunction_date.strftime('%Y-%m-%d')
