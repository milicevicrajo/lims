from datetime import datetime, timedelta
from equipment.models import Equipment, Calibration
from django.db.models import OuterRef, Subquery, F


def get_upcoming_calibrations(user):
    user_laboratories = user.laboratory_permissions.all()

    current_date = datetime.today().date()
    one_month_from_now = current_date + timedelta(days=30)

    # IDs of equipment that are active and belong to user’s laboratories
    equipment_ids = Equipment.objects.filter(
        is_rashodovana=False,
        responsible_laboratory__in=user_laboratories
    ).values_list('id', flat=True)

    # Subquery to get latest calibration date
    latest_calibration_subquery = Calibration.objects.filter(
        equipment_id=OuterRef('equipment_id')
    ).order_by('-next_calibration_date').values('next_calibration_date')[:1]

    # Annotate and filter calibrations
    calibrations_with_latest_date = Calibration.objects.annotate(
        latest_calibration_date=Subquery(latest_calibration_subquery)
    )

    upcoming_expirations = calibrations_with_latest_date.filter(
        latest_calibration_date__lte=one_month_from_now,
        latest_calibration_date=F('next_calibration_date'),
        equipment_id__in=equipment_ids
    )

    return upcoming_expirations
