from django import forms
from .models import Document, DocumentVersion
from methods.models import Method
from equipment.models import Equipment
from django_select2.forms import Select2Widget, Select2MultipleWidget


class DocumentForm(forms.ModelForm):
    related_methods = forms.ModelMultipleChoiceField(
        queryset=Method.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Povezane metode",
        required=False  # ✅ sada nije obavezno
    )
    related_equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Povezana oprema",
        required=False  # ✅ sada nije obavezno
    )

    class Meta:
        model = Document
        fields = ['code', 'title', 'type', 'description', 'laboratory', 'related_methods', 'related_equipment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['laboratory'].required = False  # ✅ i laboratorija nije obavezna u formi



class DocumentVersionForm(forms.ModelForm):    
    BOOLEAN_CHOICES = (
        ('true', 'Da'),
        ('false', 'Ne'),
    )

    issued_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum izdavanja"
    )
    valid_until = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Važi do",
    )
    
    is_current = forms.TypedChoiceField(
        label="Aktivana verzija",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == 'true',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = DocumentVersion
        fields = ['version_number', 'file', 'issued_date', 'valid_until', 'is_current', 'change_description']
        widgets = {
            'change_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
