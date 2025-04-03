from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from equipment.models import Equipment, Calibration
from datetime import datetime, timedelta
from django.db.models import OuterRef, Subquery, F
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomUser, Laboratory, Center, OrganizationalUnit
from .forms import CustomUserCreationForm, CenterForm, OrganizationalUnitForm, LaboratoryForm
from django.views.generic.edit import UpdateView, DeleteView

### CENTER ###
class CenterListView(ListView):
    model = Center
    template_name = 'core/center_list.html'
    context_object_name = 'centers'

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
class OrgUnitListView(ListView):
    model = OrganizationalUnit
    template_name = 'core/orgunit_list.html'
    context_object_name = 'orgunits'

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

class LaboratoryCreateView(CreateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('laboratory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj laboratoriju'  # Set your custom title here
        context['submit_button_label'] = 'Potvrdi'
        return context

class LaboratoryUpdateView(UpdateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('laboratory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj novog korisnika'  # Set your custom title here
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

### LIST VIEW
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'core/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'


### CREATE VIEW
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
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        form.save_m2m()
        return super().form_valid(form)


### UPDATE VIEW
class CustomUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserCreationForm  # napravi ovaj form ako ti treba
    template_name = 'generic_form.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Izmeni korisnika')
        context['submit_button_label'] = _('Sačuvaj izmene')
        return context


### DELETE VIEW
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

@login_required
def index(request):
    # Assume user is logged in and user object is available
    user = request.user
    user_laboratories = user.laboratory_permissions.all()

    # Get current date and date one month from now
    current_date = datetime.today().date()
    one_month_from_now = current_date + timedelta(days=30)

    # Get equipment IDs where rashodovana is False and laboratory is in user's laboratories
    equipment_ids = Equipment.objects.filter(
        is_rashodovana=False,
        laboratory__in=user_laboratories
    ).values_list('id', flat=True)

    # Subquery to get the latest calibration date for each equipment
    latest_calibration_subquery = Calibration.objects.filter(
        equipment_id=OuterRef('equipment_id')
    ).order_by('-next_calibration_date').values('next_calibration_date')[:1]

    # Annotate each calibration with the latest calibration date for its equipment
    calibrations_with_latest_date = Calibration.objects.annotate(
        latest_calibration_date=Subquery(latest_calibration_subquery)
    )

    # Filter calibrations to get those expiring in the next 30 days or already expired
    upcoming_expirations = calibrations_with_latest_date.filter(
        latest_calibration_date__lte=one_month_from_now,
        latest_calibration_date=F('next_calibration_date'),
        equipment_id__in=equipment_ids
    )

    # Print the results for debugging
    print(upcoming_expirations)

    # # Create forms
    # pomocna_form = PomocnaEquipmentGroupForm()
    # plan_form = EquipmentGroupForm()

    context = {
        'upcoming_calibrations': upcoming_expirations,
        # 'pomocna_form': pomocna_form,
        # 'plan_form': plan_form
    }
    return render(request, 'core/index.html', context)