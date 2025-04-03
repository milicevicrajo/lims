import django_filters
from .models import Document, DocumentType
from core.models import Laboratory
from methods.models import Method
from equipment.models import Equipment
from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget


class DocumentFilter(django_filters.FilterSet):
    type = django_filters.ModelChoiceFilter(
        queryset=DocumentType.objects.all(),
        label="Tip dokumenta",
        empty_label="Svi tipovi",
    )
    laboratory = django_filters.ModelChoiceFilter(
        queryset=Laboratory.objects.all(),
        label="Laboratorija",
    )
    # related_methods = django_filters.ModelMultipleChoiceFilter(
    #     queryset=Method.objects.all(),
    #     label="Metode",
    #     widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    # )
    # related_equipment = django_filters.ModelMultipleChoiceFilter(
    #     queryset=Equipment.objects.all(),
    #     label="Oprema",
    #     widget=Select2MultipleWidget
    # )
    is_active = django_filters.BooleanFilter(
        label="Status",
        widget=forms.Select(choices=[('', '—'), (True, 'Aktivan'), (False, 'Neaktivan')])
    )

    class Meta:
        model = Document
        fields = ['type', 'laboratory', 'is_active']

