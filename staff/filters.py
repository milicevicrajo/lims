from django import forms
import django_filters
from .models import JobPosition

class JobTypeFilter(django_filters.FilterSet):
    type_choices = [
        ('research', "Istraživačka radna mesta"),
        ('technical', "Radna mesta za obavljanje stručnih tehničkih poslova"),
    ]

    job_type = django_filters.ChoiceFilter(
        choices=type_choices,
        empty_label='Sve pozicije'
        )

    class Meta:
            model = JobPosition
            fields = ['job_type']