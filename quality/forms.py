from django import forms
from django.forms import inlineformset_factory
from django_select2.forms import Select2Widget, Select2MultipleWidget
from core.forms import UserQuerysetMixin
from core.models import Laboratory
from staff.models import Staff
from methods.models import Method
from .models import PTScheme, PTSchemeMethod, ControlTesting, ControlTestingMethod, MeasurementUncertainty

class PTSchemeMethodForm(UserQuerysetMixin,forms.ModelForm):
    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    class Meta:
        model = PTSchemeMethod
        exclude = ['pt_scheme'] 
        fields = ['method', 'number_of_participants', 'z_score', 'staff', 'measures_taken']
        
class SelectMethodCountForm(forms.Form):
    number_of_methods = forms.IntegerField(
        label="Broj metoda",
        min_value=1,
        max_value=20,  # Set an upper limit if necessary
        initial=3  # Default number of forms, can be adjusted
    )

PTSchemeMethodFormSet = inlineformset_factory(
    PTScheme, PTSchemeMethod, form=PTSchemeMethodForm,
    extra=3,  # Adjust the number to display more empty forms initially
    can_delete=True  # Allows the user to delete methods if needed
)

class PTSchemeForm(UserQuerysetMixin, forms.ModelForm):
    final_report_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum završnog izveštaja"
    )
    laboratory = forms.ModelChoiceField(
        queryset=Laboratory.objects.none(),  # Početno prazno
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Laboratorija"
    )

    class Meta:
        model = PTScheme
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        print("INIT FORMA: User je:", user)
        super().__init__(*args, **kwargs)

        if user:
            print("Korisnik postoji u formi!")

            self.apply_user_filtering(user)

        if self.instance.id and 'report_date' in self.fields:
            self.initial['report_date'] = self.instance.report_date.strftime('%Y-%m-%d')




# Form for ControlTesting
class ControlTestingForm(forms.ModelForm):
    report_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum završnog izveštaja"
    )
    laboratory = forms.ModelChoiceField(
        queryset=Laboratory.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Laboratorija"
    )
    class Meta:
        model = ControlTesting
        fields = ['laboratory', 'report_number', 'report_date', 'document']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['report_date'] = self.instance.report_date.strftime('%Y-%m-%d')

# Form for ControlTestingMethod
class ControlTestingMethodForm(forms.ModelForm):
    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    method = forms.ModelChoiceField(
        queryset=Method.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Metoda"
    )
    class Meta:
        model = ControlTestingMethod
        fields = ['method', 'number_of_participants', 'staff', 'measures_taken']

# Inline formset to handle multiple ControlTestingMethod forms
ControlTestingMethodFormSet = inlineformset_factory(
    ControlTesting, ControlTestingMethod, form=ControlTestingMethodForm,
    extra=3,  # Adjust the number to display more empty forms initially
    can_delete=True  # Allows the user to delete methods if needed
)

class MeasurementUncertaintyForm(forms.ModelForm):
    calculation_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum proračuna"
    )
    class Meta:
        model = MeasurementUncertainty
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updateda
            self.initial['calculation_date'] = self.instance.calculation_date.strftime('%Y-%m-%d')

