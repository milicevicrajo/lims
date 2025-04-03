import django_filters
from .models import Equipment
from core.models import Laboratory, OrganizationalUnit, Center

class EquipmentFilter(django_filters.FilterSet):
    type_choices2 = [
        ('Glavna', 'Glavna'),
        ('Pomocna', 'Pomocna'),
    ]

    responsible_laboratory = django_filters.ModelChoiceFilter(
        queryset=Laboratory.objects.all(),
        label="Laboratorija",
        empty_label="Sve laboratorije"
    )

    equipment_type = django_filters.ChoiceFilter(
        choices=type_choices2,
        initial='Glavna',
        empty_label="Sva oprema",
        label="Tip opreme"
    )

    organizational_unit = django_filters.ModelChoiceFilter(
        field_name='responsible_laboratory__organizational_unit',
        queryset=OrganizationalUnit.objects.all(),
        label='Organizaciona jedinica',
        empty_label='Sve jedinice'
    )

    center = django_filters.ModelChoiceFilter(
        field_name='responsible_laboratory__organizational_unit__center',
        queryset=Center.objects.all(),
        label='Centar',
        empty_label='Svi centri'
    )

    class Meta:
        model = Equipment
        fields = ['center', 'organizational_unit', 'responsible_laboratory', 'equipment_type', 'group']

    

class UserLabEquipmentFilter(django_filters.FilterSet):
    type_choices2 = [
        ('Glavna', 'Glavna'),
        ('Pomocna', 'Pomocna'),
    ]

    equipment_type = django_filters.ChoiceFilter(choices=type_choices2, initial='Glavna')
    name = django_filters.CharFilter(lookup_expr='icontains', label='Naziv opreme')

    class Meta:
        model = Equipment
        fields = ['card_number', 'name', 'equipment_type', 'group']