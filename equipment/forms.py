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
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum nabavke"
    )
    usage_start_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum stavljanja u upotrebu"
    )
    
    main_equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(equipment_type = "Glavna"),
        widget=Select2Widget(),
        label="Glavna oprema"
    )

    class Meta:
        model = Equipment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Ensure that user is passed to the form
        super().__init__(*args, **kwargs)
        self.fields['main_equipment'].required = False  # Explicitly setting required to False

        if user and user.laboratory:
            org_unit = user.laboratory.organizational_unit
            self.fields['main_equipment'].queryset = Equipment.objects.filter(
                equipment_type="Glavna",
                responsible_laboratory__organizational_unit=org_unit
            ).distinct()


        if self.instance.id:  # Check if instance is being updated
            self.initial['purchase_date'] = self.instance.purchase_date.strftime('%Y-%m-%d')
            self.initial['usage_start_date'] = self.instance.usage_start_date.strftime('%Y-%m-%d')

        if user and user.is_superuser or user.role == 'admin':
            self.fields['responsible_laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.all(),
                required=True,
                label="Odgovorna laboratorija",
                widget=Select2Widget(attrs={'class': 'select2-method'}),
            )
        else:
            # Automatically set the responsible laboratory for non-superusers if not already set
            self.fields['responsible_laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.filter(id=user.laboratory.id),
                initial=user.laboratory.id,
                label="Odgovorna laboratorija",
                widget=forms.HiddenInput(),  # Hide field for non-superusers
                required=False
                )
            self.instance.responsible_laboratory = user.laboratory

    def clean_laboratory(self):
        laboratory = self.cleaned_data.get('laboratory', [])
        return laboratory
    
    def clean(self):
        cleaned_data = super().clean()
        card_number = cleaned_data.get('card_number')
        responsible_laboratory = cleaned_data.get('responsible_laboratory')

        if card_number and responsible_laboratory:
            org_unit = responsible_laboratory.organizational_unit

            if Equipment.objects.filter(
                card_number=card_number,
                responsible_laboratory__organizational_unit=org_unit
            ).exclude(pk=self.instance.pk).exists():
                raise ValidationError({
                    'card_number': "Broj kartona već postoji u organizacionoj jedinici."
                })

        return cleaned_data

    
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

    # def clean_equipment(self):
    #     equipment = self.cleaned_data.get('equipment')
    #     if equipment.responsible_laboratory != self.user.laboratory:
    #         print(equipment.responsible_laboratory,self.user.laboratory)
    #         raise forms.ValidationError("This equipment does not belong to your laboratory.")
    #     return equipment

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
