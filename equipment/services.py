import io
from django.db.models import OuterRef, Subquery
import qrcode
from equipment.models import Equipment, Calibration, InternalControl, Repair
from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import F

def get_rashodovana_oprema_for_user(user):
    if not user.is_authenticated:
        return Equipment.objects.none()

    queryset = Equipment.objects.filter(
        responsible_laboratory__in=user.laboratory_permissions.all(),
        is_rashodovana=True
    )

    queryset = annotate_next_calibration_date(queryset)

    return queryset

def get_user_laboratory_equipment(user):
    if user.is_authenticated and user.laboratory:
        queryset = Equipment.objects.filter(
            responsible_laboratory=user.laboratory,
            is_rashodovana=False
        )
        return annotate_next_calibration_date(queryset)
    else:
        return Equipment.objects.none()

def get_user_equipment_queryset(user):
    if user.is_authenticated:
        if user.is_superuser:
            queryset = Equipment.objects.filter(is_rashodovana=False)
        elif user.laboratory_permissions.exists():
            org_units = user.laboratory_permissions.values_list('organizational_unit', flat=True)
            queryset = Equipment.objects.filter(
                responsible_laboratory__organizational_unit__in=org_units,
                is_rashodovana=False
            )
        else:
            queryset = Equipment.objects.none()

        return annotate_next_calibration_date(queryset)
    return Equipment.objects.none()



def calculate_equipment_calibration_scores(equipment):
    latest_calibration = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date').first()
    if not latest_calibration:
        return None

    selected_interval, calculated_interval, ocena1, ocena2, ocena3, ocena4, ocena5 = latest_calibration.calculate_calibration_interval()

    return {
        'selected_interval': selected_interval,
        'calculated_interval': calculated_interval,
        'ocena1': round(ocena1 * 0.2, 3),
        'ocena2': round(ocena2 * 0.2, 3),
        'ocena3': round(ocena3 * 0.1, 3),
        'ocena4': round(ocena4 * 0.3, 3),
        'ocena5': round(ocena5 * 0.2, 3),
        'korekcioni_faktor': round((ocena1*0.2 + ocena2*0.2 + ocena3*0.1 + ocena4*0.3 + ocena5*0.2), 2),
    }

def get_internal_controls_with_devices(equipment, limit=5):
    internal_controls = InternalControl.objects.filter(equipment=equipment).order_by('-last_control_date')[:limit]
    return [
        {
            'internal_control': control,
            'controlling_devices': control.controlling_devices.all()
        }
        for control in internal_controls
    ]

def annotate_next_calibration_date(queryset):
    next_calibration_date_subquery = Calibration.objects.filter(
        equipment_id=OuterRef('pk')
    ).order_by('-calibration_date').values('next_calibration_date')[:1]

    return queryset.annotate(next_calibration_date=Subquery(next_calibration_date_subquery))


def generate_equipment_qr_data(equipment, request):
    qr_data = f"{request.build_absolute_uri('/')[:-1]}{equipment.get_absolute_url()}"
    qr = qrcode.make(qr_data)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


# 🔵 Equipment servis
def create_equipment(data, user):
    # Izdvoji laboratorije pre nego što praviš instancu
    laboratory_data = data.pop('laboratory', [])

    equipment = Equipment(**data)
    equipment.save()

    if laboratory_data:
        equipment.laboratory.set(laboratory_data)

    return equipment


def update_equipment(equipment, form):
    equipment = form.save(commit=False)
    equipment.save()
    form.save_m2m()  # Ako imaš ManyToMany polja
    return equipment


def toggle_equipment_status(equipment):
    equipment.is_rashodovana = not equipment.is_rashodovana
    equipment.save()
    return equipment

def update_pomocna_equipment(main_equipment, selected_equipment_id, action):
    try:
        selected_equipment = Equipment.objects.get(id=selected_equipment_id)
    except Equipment.DoesNotExist:
        return {'success': False, 'message': 'Oprema nije pronađena'}

    if action == 'add':
        selected_equipment.main_equipment = main_equipment
        message = f'Oprema {selected_equipment} dodata u pomoćnu opremu.'
    elif action == 'remove':
        selected_equipment.main_equipment = None
        message = f'Oprema {selected_equipment} uklonjena iz pomoćne opreme.'
    else:
        return {'success': False, 'message': 'Nevažeća akcija'}

    selected_equipment.save()

    return {'success': True, 'message': message, 'equipment_id': selected_equipment.id, 'action': action}


# 🔵 Calibration servis
def get_latest_calibrations_for_user(user):
    if not user.is_authenticated or not user.laboratory_permissions.exists():
        return Calibration.objects.none()

    equipment_ids = Equipment.objects.filter(
        responsible_laboratory__in=user.laboratory_permissions.all()
    ).values_list('id', flat=True)

    latest_calibration_date_subquery = Calibration.objects.filter(
        equipment_id=OuterRef('equipment_id')
    ).order_by('-calibration_date').values('calibration_date')[:1]

    latest_calibrations = Calibration.objects.filter(
        equipment_id__in=equipment_ids
    ).annotate(
        latest_calibration_date=Subquery(latest_calibration_date_subquery)
    ).filter(
        calibration_date=F('latest_calibration_date')
    )

    return latest_calibrations

def create_calibration(data, user):
    try:
        with transaction.atomic():
            calibration = Calibration(**data)
            calibration.user = user
            calibration.save()
            return calibration
    except IntegrityError:
        raise ValidationError("Broj sertifikata već postoji.")

def update_calibration(calibration, data, user):
    for field, value in data.items():
        setattr(calibration, field, value)
    calibration.user = user

    try:
        calibration.save()
        return calibration
    except IntegrityError:
        raise ValidationError("Broj sertifikata već postoji.")


# 🔵 Internal Control servis
def create_internal_control(data, user):
    internal_control = InternalControl(**data)
    internal_control.user = user

    try:
        internal_control.save()
        return internal_control
    except IntegrityError:
        raise ValidationError("Došlo je do greške prilikom čuvanja interne kontrole.")

def update_internal_control(internal_control, data, user):
    for field, value in data.items():
        setattr(internal_control, field, value)

    internal_control.user = user

    try:
        internal_control.save()
        return internal_control
    except Exception as e:
        raise ValidationError(f'Greška prilikom ažuriranja interne kontrole: {str(e)}')


def add_controlling_device(internal_control, equipment):
    internal_control.controlling_devices.add(equipment)
    internal_control.save()
    return 'Added'

def remove_controlling_device(internal_control, equipment):
    internal_control.controlling_devices.remove(equipment)
    internal_control.save()
    return 'Removed'


# 🔵 Repair servis

def create_repair(data, user):
    repair = Repair(**data)
    repair.user = user

    try:
        repair.save()
    except Exception as e:
        raise ValidationError(f'Greška prilikom čuvanja popravke: {str(e)}')

    return repair


def update_repair(repair_instance, data, user):
    for field, value in data.items():
        setattr(repair_instance, field, value)

    repair_instance.user = user  # Uvek postavljamo korisnika koji pravi izmenu

    try:
        repair_instance.save()
    except Exception as e:
        raise ValidationError(f'Greška prilikom ažuriranja popravke: {str(e)}')