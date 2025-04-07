import django_filters
from core.models import Laboratory, Center, OrganizationalUnit
from .models import Method
class MethodFilter(django_filters.FilterSet):
    center = django_filters.ModelChoiceFilter(
        field_name='laboratory__organizational_unit__center',
        queryset=Center.objects.all(),
        label='Centar',
        empty_label='Svi centri'
    )

    org_unit = django_filters.ModelChoiceFilter(
        field_name='laboratory__organizational_unit',
        queryset=OrganizationalUnit.objects.all(),
        label='Organizaciona jedinica',
        empty_label='Sve organizacione jedinice'
    )

    laboratory = django_filters.ModelChoiceFilter(
        queryset=Laboratory.objects.all(),
        label="Laboratorija",
        empty_label="Sve laboratorije"
    )

    class Meta:
        model = Method
        fields = ['center', 'org_unit', 'laboratory']
