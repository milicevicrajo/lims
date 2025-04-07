from datetime import date
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from .models import NoMethodAuthorization, Staff, StaffJobPosition, ProfessionalExperience, TrainingCourse, MembershipInInternationalOrg
from .models import Authorization, StaffMethodTraining, Training
from django.urls import reverse_lazy
from .models import AuthorizationType

def get_active_staff_queryset():
    queryset = Staff.objects.prefetch_related('staffjobposition_set__job_position')
    queryset = queryset.filter(staffjobposition__end_date__isnull=True).distinct()

    today = date.today()
    for staff in queryset:
        staff.years_experience = calculate_years_of_experience(staff.start_date_in_profession, today)
    return queryset

def calculate_years_of_experience(start_date, today):
    if start_date:
        return today.year - start_date.year - (
            (today.month, today.day) < (start_date.month, start_date.day)
        )
    return None

def get_staff_detail_context(staff):
    today = date.today()

    years_experience = calculate_years_of_experience(staff.start_date_in_profession, today)
    years_experience_ims = calculate_years_of_experience(staff.start_date_in_ims, today)

    fields = [
        (field.verbose_name, getattr(staff, field.name))
        for field in Staff._meta.fields
        if not field.name.startswith('_') and field.name != 'id'
    ]

    return {
        'fields': fields,
        'job_positions': StaffJobPosition.objects.filter(staff=staff),
        'professional_experience': ProfessionalExperience.objects.filter(staff=staff),
        'training_courses': TrainingCourse.objects.filter(staff=staff),
        'membership_in_orgs': MembershipInInternationalOrg.objects.filter(staff=staff),
        'years_experience': years_experience,
        'years_experience_ims': years_experience_ims,
        'authorizations': Authorization.objects.filter(staff=staff),
        'method_trainings': StaffMethodTraining.objects.filter(staff=staff),
        'no_method_trainings': Training.objects.filter(staff=staff, methods__isnull=True),
    }

def get_staff_object(pk):
    return get_object_or_404(Staff, pk=pk)

from .models import JobPosition, StaffJobPosition
from django.shortcuts import get_object_or_404

# Job Position services

def get_job_position_object(pk):
    return get_object_or_404(JobPosition, pk=pk)

def get_job_position_context():
    return {
        'title': 'Spisak radnih mesta po "Pravilniku o sistematizaciji poslova"'
    }

# Staff Job Position services

def get_staff_job_position_initial(kwargs):
    staff_id = kwargs.get('staff_id')
    if staff_id:
        return {'staff': staff_id}
    return {}

def get_staff_job_position_success_url(instance):
    return reverse_lazy('staff_detail', kwargs={'pk': instance.staff.id})

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import (
    ProfessionalExperience,
    TrainingCourse,
    MembershipInInternationalOrg,
    Staff
)
def get_staff_job_position_object(pk):
    return get_object_or_404(StaffJobPosition, pk=pk)

def get_staff_job_position_success_url(instance):
    return reverse_lazy('staff_detail', kwargs={'pk': instance.staff.id})
# --- Professional Experience services ---

def get_professional_experience_object(pk):
    return get_object_or_404(ProfessionalExperience, pk=pk)

def get_professional_experience_initial(kwargs):
    staff_id = kwargs.get('staff_id')
    if staff_id:
        staff = get_object_or_404(Staff, id=staff_id)
        return {'staff': staff}
    return {}

def get_professional_experience_success_url(instance):
    return reverse_lazy('staff_detail', kwargs={'pk': instance.staff.id})

# --- Training Course services ---

def get_training_course_object(pk):
    return get_object_or_404(TrainingCourse, pk=pk)

def get_training_course_initial(kwargs):
    staff_id = kwargs.get('staff_id')
    if staff_id:
        staff = get_object_or_404(Staff, id=staff_id)
        return {'staff': staff}
    return {}

def get_training_course_success_url(instance):
    return reverse_lazy('staff_detail', kwargs={'pk': instance.staff.id})

# --- Membership in International Org services ---

def get_membership_object(pk):
    return get_object_or_404(MembershipInInternationalOrg, pk=pk)

def get_membership_initial(kwargs):
    staff_id = kwargs.get('staff_id')
    if staff_id:
        staff = get_object_or_404(Staff, id=staff_id)
        return {'staff': staff}
    return {}

def get_membership_success_url(instance):
    return reverse_lazy('staff_detail', kwargs={'pk': instance.staff.id})

from .models import Training, StaffMethodTraining, TrainingTests
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

# --- Training services ---

def get_training_object(pk):
    return get_object_or_404(Training, pk=pk)

def create_staff_method_trainings(training):
    methods = training.methods.all()
    staff_members = training.staff.all()

    if methods.exists() and staff_members.exists():
        for staff in staff_members:
            for method in methods:
                StaffMethodTraining.objects.get_or_create(
                    staff=staff, method=method, training=training
                )

def get_training_success_url():
    return reverse_lazy('training_list')

def get_training_test_success_url(request):
    next_url = request.GET.get('next')
    if next_url:
        return next_url
    return reverse_lazy('training_list')

# --- AuthorizationType services ---

def get_authorization_type_object(pk):
    return get_object_or_404(AuthorizationType, pk=pk)

def get_authorization_type_success_url():
    return reverse_lazy('authorization_type_list')


# --- Authorization services ---

def create_authorizations(staff_members, methods, authorization_types, date):
    created_count = 0
    for staff in staff_members:
        for method in methods:
            for auth_type in authorization_types:
                try:
                    Authorization.objects.create(
                        staff=staff,
                        method=method,
                        authorization_type=auth_type,
                        date=date
                    )
                    created_count += 1
                except IntegrityError:
                    continue
    return created_count

def get_authorization_object(pk):
    return get_object_or_404(Authorization, pk=pk)

def get_authorization_success_url(request):
    next_url = request.GET.get('next')
    if next_url:
        return next_url
    return reverse_lazy('authorization_list')

# --- NoMethodAuthorization services ---

def get_no_method_authorization_object(pk):
    return get_object_or_404(NoMethodAuthorization, pk=pk)

def get_no_method_authorization_success_url(request):
    next_url = request.GET.get('next')
    if next_url:
        return next_url
    return reverse_lazy('no_method_authorization_list')