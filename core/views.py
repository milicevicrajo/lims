from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from core.services import get_all_centers
from equipment.models import Equipment, Calibration
from datetime import datetime, timedelta
from django.db.models import OuterRef, Subquery, F
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomUser, Laboratory, Center, OrganizationalUnit
from .forms import CustomUserCreationForm, CenterForm, OrganizationalUnitForm, LaboratoryForm
from django.views.generic.edit import UpdateView, DeleteView
from .services import (
    get_all_organizational_units,
    get_all_laboratories,
)

### CENTER ###
class CenterListView(ListView):
    model = Center
    template_name = 'core/center_list.html'
    context_object_name = 'centers'

    def get_queryset(self):
        return get_all_centers()

class CenterCreateView(CreateView):
    model = Center
    form_class = CenterForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('center_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj centar'
        context['submit_button_label'] = 'Potvrdi'
        return context

class CenterUpdateView(UpdateView):
    model = Center
    form_class = CenterForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('center_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Prepravi centar'
        context['submit_button_label'] = 'Potvrdi'
        return context

class CenterDeleteView(DeleteView):
    model = Center
    template_name = 'core/center_confirm_delete.html'
    success_url = reverse_lazy('center_list')

### ORGANIZATIONAL UNIT ###
# Organizational Unit Views
class OrgUnitListView(ListView):
    model = OrganizationalUnit
    template_name = 'core/orgunit_list.html'
    context_object_name = 'orgunits'

    def get_queryset(self):
        return get_all_organizational_units()

class OrgUnitCreateView(CreateView):
    model = OrganizationalUnit
    form_class = OrganizationalUnitForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('orgunit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj organizacionu jedinicu'
        context['submit_button_label'] = 'Potvrdi'
        return context

class OrgUnitUpdateView(UpdateView):
    model = OrganizationalUnit
    form_class = OrganizationalUnitForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('orgunit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Prepravi organizacionu jedinicu'
        context['submit_button_label'] = 'Potvrdi'
        return context

class OrgUnitDeleteView(DeleteView):
    model = OrganizationalUnit
    template_name = 'core/orgunit_confirm_delete.html'
    success_url = reverse_lazy('orgunit_list')

### LABORATORY ###
class LaboratoryListView(ListView):
    model = Laboratory
    template_name = 'core/laboratory_list.html'
    context_object_name = 'laboratories'

    def get_queryset(self):
        return get_all_laboratories()

class LaboratoryCreateView(CreateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('laboratory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj laboratoriju'
        context['submit_button_label'] = 'Potvrdi'
        return context

class LaboratoryUpdateView(UpdateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('laboratory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Prepravi laboratoriju'
        context['submit_button_label'] = 'Potvrdi'
        return context

class LaboratoryDeleteView(DeleteView):
    model = Laboratory
    template_name = 'core/laboratory_confirm_delete.html'
    success_url = reverse_lazy('laboratory_list')

### USER ###
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.utils.translation import gettext_lazy as _

from .services import get_all_users, create_user, update_user

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'core/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'

    def get_queryset(self):
        return get_all_users()


class CustomUserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Dodaj novog korisnika')
        context['submit_button_label'] = _('Kreiraj korisnika')
        return context

    def form_valid(self, form):
        create_user(form)
        return super().form_valid(form)


class CustomUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Izmeni korisnika')
        context['submit_button_label'] = _('Sačuvaj izmene')
        return context

    def form_valid(self, form):
        update_user(form)
        return super().form_valid(form)


class CustomUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomUser
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.is_superuser



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Set the session key in the user model
            user.session_key = request.session.session_key
            user.save()
            return redirect('index')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'core/login.html')

# @csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('login_route')  # ili neka druga početna stranica

def error404(request):  
    return render(request, 'core/error404.html')

