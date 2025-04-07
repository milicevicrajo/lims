from equipment.models import Equipment
from quality.models import ControlTestingMethod, MeasurementUncertainty, PTSchemeMethod
from staff.models import Authorization, Training
from .models import Standard, TestSubject, TestingArea, SubDiscipline, Method
from django.core.exceptions import ValidationError
from django.db import IntegrityError

def create_standard(data):
    standard = Standard(**data)
    try:
        standard.save()
        return standard
    except IntegrityError:
        raise ValidationError("Standard sa ovom oznakom već postoji.")

def update_standard(instance, data):
    for attr, value in data.items():
        setattr(instance, attr, value)
    try:
        instance.save()
        return instance
    except IntegrityError:
        raise ValidationError("Došlo je do greške prilikom ažuriranja standarda.")

def delete_standard(instance):
    instance.delete()


def create_testing_area(data):
    testing_area = TestingArea(**data)
    try:
        testing_area.save()
        return testing_area
    except IntegrityError:
        raise ValidationError("Oblast ispitivanja sa ovim kodom već postoji.")

def update_testing_area(instance, data):
    for attr, value in data.items():
        setattr(instance, attr, value)
    try:
        instance.save()
        return instance
    except IntegrityError:
        raise ValidationError("Greška prilikom ažuriranja oblasti ispitivanja.")

def delete_testing_area(instance):
    instance.delete()


# ==== Test Subject Services ====

def create_test_subject(data):
    test_subject = TestSubject(**data)
    try:
        test_subject.save()
        return test_subject
    except IntegrityError:
        raise ValidationError("Predmet ispitivanja sa ovim kodom već postoji.")

def update_test_subject(instance, data):
    for attr, value in data.items():
        setattr(instance, attr, value)
    try:
        instance.save()
        return instance
    except IntegrityError:
        raise ValidationError("Greška prilikom ažuriranja predmeta ispitivanja.")

def delete_test_subject(instance):
    instance.delete()


def create_method(data, user):
    method = Method(**data)
    method.laboratory = user.laboratory  # povezujemo metodu sa laboratorijom korisnika
    try:
        method.save()
        # Ako ima M2M polja, mora posebno:
        if 'standard_secondary' in data:
            method.standard_secondary.set(data['standard_secondary'])
        if 'equipment' in data:
            method.equipment.set(data['equipment'])
        return method
    except IntegrityError:
        raise ValidationError("Metoda sa unetim podacima već postoji ili postoji problem sa bazom.")

def update_method(instance, data):
    for attr, value in data.items():
        if attr in ['standard_secondary', 'equipment']:
            continue  # skip M2M za sad
        setattr(instance, attr, value)
    try:
        instance.save()
        # update M2M after save
        if 'standard_secondary' in data:
            instance.standard_secondary.set(data['standard_secondary'])
        if 'equipment' in data:
            instance.equipment.set(data['equipment'])
        return instance
    except IntegrityError:
        raise ValidationError("Greška prilikom ažuriranja metode.")

def delete_method(instance):
    instance.delete()


def get_method_detail_context(method):
    return {
        'equipment_list': method.equipment.all(),
        'authorizations': Authorization.objects.filter(method=method),
        'trainings': Training.objects.filter(methods__in=[method]),
        'control_tests': ControlTestingMethod.objects.filter(method=method),
        'pt_activity': PTSchemeMethod.objects.filter(method=method),
        'measurement_uncertainty': MeasurementUncertainty.objects.filter(method=method),
    }

def update_method_equipment(method, equipment_id, action):
    try:
        equipment = Equipment.objects.get(id=equipment_id)
    except Equipment.DoesNotExist:
        return {'error': 'Equipment not found'}

    if action == 'add':
        method.equipment.add(equipment)
        message = 'Oprema dodata u metodu'
    elif action == 'remove':
        method.equipment.remove(equipment)
        message = 'Oprema uklonjena iz metode'
    else:
        return {'error': 'Invalid action'}

    method.save()
    return {'message': message, 'equipment_id': equipment_id, 'action': action}

def get_user_equipment_queryset_for_method(user):
    if user.is_authenticated and user.laboratory_permissions.exists():
        org_units = user.laboratory_permissions.values_list('organizational_unit', flat=True)
        return Equipment.objects.filter(
            responsible_laboratory__organizational_unit__in=org_units,
            equipment_type='Glavna',
            is_rashodovana=False
        )
    return Equipment.objects.filter(
        equipment_type='Glavna',
        is_rashodovana=False
    )

from .models import SubDiscipline

def create_subdiscipline(data):
    return SubDiscipline.objects.create(**data)

def update_subdiscipline(instance, data):
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()
    return instance

def delete_subdiscipline(pk):
    subdiscipline = SubDiscipline.objects.get(pk=pk)
    subdiscipline.delete()
    return True

def get_subdiscipline_methods(subdiscipline):
    return subdiscipline.method_set.all()  # ili Method.objects.filter(subdiscipline=subdiscipline)
