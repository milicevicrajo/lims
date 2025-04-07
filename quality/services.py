from gettext import translation
from django.forms import inlineformset_factory
from quality.forms import ControlTestingForm, PTSchemeForm, PTSchemeMethodForm
from .models import PTScheme, PTSchemeMethod
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import ControlTesting, ControlTestingMethod
from .forms import ControlTestingForm, ControlTestingMethodForm

def get_all_pt_schemes():
    return PTScheme.objects.all()

def get_pt_scheme_fields(pt_scheme):
    return [
        (field.verbose_name, getattr(pt_scheme, field.name))
        for field in PTScheme._meta.fields
        if not field.name.startswith('_') and field.name != 'id'
    ]

def create_pt_scheme(data, files):
    form = PTSchemeForm(data, files)
    if form.is_valid():
        return form.save(), None
    return None, form.errors

# Kreiranje formset factory funkcije
def create_pt_scheme_method_formset_factory(number_of_methods):
    return inlineformset_factory(
        PTScheme,
        PTSchemeMethod,
        form=PTSchemeMethodForm,
        extra=number_of_methods,
        can_delete=True
    )

# Kreiranje praznog formset-a
def get_empty_pt_scheme_method_formset(number_of_methods):
    FormSet = create_pt_scheme_method_formset_factory(number_of_methods)
    return FormSet()

# Validacija i čuvanje scheme i metode u formset-u
def process_pt_scheme_form(request_data, request_files, number_of_methods, user=None):
    FormSet = create_pt_scheme_method_formset_factory(number_of_methods)

    scheme_form = PTSchemeForm(request_data, request_files, user=user)
    method_formset = FormSet(request_data, request_files, user=user)

    if scheme_form.is_valid() and method_formset.is_valid():
        pt_scheme = scheme_form.save()
        method_formset.instance = pt_scheme
        method_formset.save()
        return pt_scheme, None, None

    return None, scheme_form, method_formset

def create_control_testing_method_formset(number_of_methods):
    return inlineformset_factory(
        ControlTesting,
        ControlTestingMethod,
        form=ControlTestingMethodForm,
        extra=number_of_methods,
        can_delete=True
    )


@transaction.atomic
def create_control_testing(data, files, number_of_methods):
    control_form = ControlTestingForm(data, files)
    ControlTestingMethodFormSet = create_control_testing_method_formset(number_of_methods)
    method_formset = ControlTestingMethodFormSet(data, files)

    if control_form.is_valid() and method_formset.is_valid():
        control_testing = control_form.save()

        method_formset.instance = control_testing
        method_formset.save()

        return control_testing, None, None
    else:
        return None, control_form, method_formset


@transaction.atomic
def update_control_testing(instance, data, files):
    form = ControlTestingForm(data, files, instance=instance)
    if form.is_valid():
        form.save()
        return True, None
    else:
        return False, form.errors


def delete_control_testing(pk):
    obj = get_object_or_404(ControlTesting, pk=pk)
    obj.delete()

from .models import MeasurementUncertainty
from django.db import transaction

@transaction.atomic
def create_measurement_uncertainty(data, user):
    instance = MeasurementUncertainty(**data)
    # Ako želiš, ovde možeš setovati dodatno user ili laboratoriju ako se prati
    instance.save()
    return instance

@transaction.atomic
def update_measurement_uncertainty(instance, data):
    for attr, value in data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance

@transaction.atomic
def delete_measurement_uncertainty(instance):
    instance.delete()
