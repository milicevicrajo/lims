from .models import Center

def get_all_centers():
    return Center.objects.all()
from .models import Center, OrganizationalUnit, Laboratory

def get_all_centers():
    return Center.objects.all()

def get_all_organizational_units():
    return OrganizationalUnit.objects.select_related('center').all()

def get_all_laboratories():
    return Laboratory.objects.select_related('organizational_unit').all()

# core/services.py

from .models import CustomUser

def get_all_users():
    return CustomUser.objects.all()

def create_user(form):
    user = form.save(commit=False)
    user.set_password(form.cleaned_data['password'])
    user.save()
    form.save_m2m()
    return user

def update_user(form):
    user = form.save(commit=False)
    if form.cleaned_data.get('password'):
        user.set_password(form.cleaned_data['password'])
    user.save()
    form.save_m2m()
    return user
