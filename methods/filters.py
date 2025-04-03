import django_filters
from .models import Method
from core.models import Laboratory

class MethodFilter(django_filters.FilterSet):
    laboratory = django_filters.ModelChoiceFilter(
        queryset=Laboratory.objects.all(),
        label="Laboratorija",
        empty_label="Sve laboratorije"
    )

    org_unit = django_filters.ChoiceFilter(
        field_name='laboratory__organizational_unit',
        label='Organizaciona jedinica',
        choices=lambda: [
            (org_unit, org_unit)
            for org_unit in Laboratory.objects.values_list('organizational_unit', flat=True).distinct()
        ],
        empty_label="Sve jedinice"
    )

    class Meta:
        model = Method
        fields = ['laboratory', 'org_unit']