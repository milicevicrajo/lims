from datetime import date
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from lims.mixins import LaboratoryPermissionMixin
from .filters import JobTypeFilter

# STAFF
@method_decorator(never_cache, name='dispatch')
class StaffListView(LaboratoryPermissionMixin, ListView):
    model = Staff
    template_name = 'staff/staff_list.html'


    def get_queryset(self):
        # Get the list of staff with active job positions
        queryset = super().get_queryset().prefetch_related('staffjobposition_set__job_position')
        queryset = queryset.filter(staffjobposition__end_date__isnull=True).distinct()

        # Calculate years of experience for each staff
        today = date.today()
        for staff in queryset:
            if staff.start_date_in_profession:
                years_experience = today.year - staff.start_date_in_profession.year - (
                    (today.month, today.day) < (staff.start_date_in_profession.month, staff.start_date_in_profession.day)
                )
                staff.years_experience = years_experience
            else:
                staff.years_experience = None

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_list = context['staff_list']
        context['title'] = 'Spisak osoblja'


        return context

class StaffCreateView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_button_label'] = 'Potvrdi'
        context['title'] = 'Dodaj novog zaposlenog'
        return context

class StaffDetailView(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = 'staff/staff_detail.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalji o osoblju'
        staff = context['staff']

        # Calculate years of experience in profession
        if staff.start_date_in_profession:
            today = date.today()
            years_experience = today.year - staff.start_date_in_profession.year - (
                (today.month, today.day) < (staff.start_date_in_profession.month, staff.start_date_in_profession.day)
            )
        else:
            years_experience = None

        # Calculate years of experience in IMS
        if staff.start_date_in_ims:
            years_experience_ims = today.year - staff.start_date_in_ims.year - (
                (today.month, today.day) < (staff.start_date_in_ims.month, staff.start_date_in_ims.day)
            )
        else:
            years_experience_ims = None

        fields = [
            (field.verbose_name, getattr(staff, field.name))
            for field in Staff._meta.fields
            if not field.name.startswith('_') and field.name != 'id'
        ]

        job_positions = StaffJobPosition.objects.filter(staff=staff)

        context['fields'] = fields
        context['job_positions'] = job_positions
        context['professional_experience'] = ProfessionalExperience.objects.filter(staff=staff)
        context['training_courses'] = TrainingCourse.objects.filter(staff=staff)
        context['membership_in_orgs'] = MembershipInInternationalOrg.objects.filter(staff=staff)
        context['years_experience'] = years_experience
        context['years_experience_ims'] = years_experience_ims
        context['authorizations'] = Authorization.objects.filter(staff=staff)
        context['method_trainings'] = StaffMethodTraining.objects.filter(staff=staff)
        context['no_method_trainings'] = Training.objects.filter(staff=staff, methods__isnull=True)
        return context
    
class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'generic_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi karton osoblja'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    
    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.id})
    
class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy('staff_list')
    def get_object(self, queryset=None):
        obj = Staff.objects.get(id=self.kwargs.get('pk'))
        return obj

# Views for JobPosition
class JobPositionListView(LoginRequiredMixin, FilterView):
    model = JobPosition
    template_name = 'staff/job_position_list.html'
    context_object_name = 'job_positions'
    filterset_class = JobTypeFilter 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak radnih mesta po "Pravilniku o sistematizaciji poslova"'
        return context

class JobPositionDetailView(DetailView):
    model = JobPosition
    template_name = 'staff/job_position_detail.html'  
    context_object_name = 'job_position'  

class JobPositionCreateView(LoginRequiredMixin, CreateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'staff/job_position_form.html'
    success_url = reverse_lazy('job_position_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj novu poziciju/radno mesto'
        context['submit_button_label'] = 'Potvrdi'
        return context

class JobPositionUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'staff/job_position_form.html'
    success_url = reverse_lazy('job_position_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi poziciju/radno mesto'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
class JobPositionDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPosition
    template_name = 'ims/job_position/job_position_confirm_delete.html'
    success_url = reverse_lazy('job_position_list')

    def get_object(self, queryset=None):
        obj = JobPosition.objects.get(id=self.kwargs.get('pk'))
        return obj

# List all job positions for staff
class StaffJobPositionListView(ListView):
    model = StaffJobPosition
    template_name = 'staff/staffjobposition_list.html'
    context_object_name = 'positions'

# Create a new job position for staff
class StaffJobPositionCreateView(CreateView):
    model = StaffJobPosition
    form_class = StaffJobPositionForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('staffjobposition_list')
    
    def get_initial(self):
        initial = super().get_initial()
        staff_id = self.kwargs.get('staff_id', None)
        if staff_id:
            initial['staff'] = Staff.objects.get(id=staff_id)
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodeli radno mesto osoblju'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})

# Update an existing job position for staff
class StaffJobPositionUpdateView(UpdateView):
    model = StaffJobPosition
    form_class = StaffJobPositionForm
    template_name = 'ims/generic_form.html'


    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})

# Delete an existing job position for staff
class StaffJobPositionDeleteView(DeleteView):
    model = StaffJobPosition

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
# Views for ProfessionalExperience
class ProfessionalExperienceListView(LoginRequiredMixin, ListView):
    model = ProfessionalExperience
    template_name = 'staff/professional_experience_list.html'
    context_object_name = 'professional_experiences'

class ProfessionalExperienceCreateView(LoginRequiredMixin, CreateView):
    model = ProfessionalExperience
    form_class = ProfessionalExperienceForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('professional_experience_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj profesionalno iskustvo'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        staff_id = self.kwargs.get('staff_id', None)
        if staff_id:
            initial['staff'] = Staff.objects.get(id=staff_id)
        return initial
    
    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
        
class ProfessionalExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfessionalExperience
    form_class = ProfessionalExperienceForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi profesionalno iskustvo'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
class ProfessionalExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = ProfessionalExperience

    def get_object(self, queryset=None):
        obj = get_object_or_404(ProfessionalExperience, id=self.kwargs.get('pk'))
        return obj

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    

# Views for TrainingCourse
class TrainingCourseListView(LoginRequiredMixin, ListView):
    model = TrainingCourse
    template_name = 'staff/training_course_list.html'
    context_object_name = 'training_courses'

class TrainingCourseCreateView(LoginRequiredMixin, CreateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('training_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj obuku/usavršavanje'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        staff_id = self.kwargs.get('staff_id', None)
        if staff_id:
            initial['staff'] = Staff.objects.get(id=staff_id)
        return initial
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
class TrainingCourseUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('training_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi obuku/usavršavanje'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
class TrainingCourseDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingCourse

    def get_object(self, queryset=None):
        obj = TrainingCourse.objects.get(id=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
# Views for MembershipInInternationalOrg
class MembershipInInternationalOrgListView(LoginRequiredMixin, ListView):
    model = MembershipInInternationalOrg
    template_name = 'staff/membership_international_org_list.html'
    context_object_name = 'memberships'

class MembershipInInternationalOrgCreateView(LoginRequiredMixin, CreateView):
    model = MembershipInInternationalOrg
    form_class = MembershipInInternationalOrgForm
    template_name = 'ims/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj članstvo u organizaciji'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        staff_id = self.kwargs.get('staff_id', None)
        if staff_id:
            initial['staff'] = Staff.objects.get(id=staff_id)
        return initial
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
class MembershipInInternationalOrgUpdateView(LoginRequiredMixin, UpdateView):
    model = MembershipInInternationalOrg
    form_class = MembershipInInternationalOrgForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi članstvo u organizaciji'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})

class MembershipInInternationalOrgDeleteView(LoginRequiredMixin, DeleteView):
    model = MembershipInInternationalOrg
    def get_object(self, queryset=None):
        obj = MembershipInInternationalOrg.objects.get(id=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.staff.id})
    
# TRAINING OBUKE
@method_decorator(never_cache, name='dispatch')
class TrainingListView(LoginRequiredMixin, ListView):
    model = Training
    template_name = 'staff/training_list.html'
    context_object_name = 'trainings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak obavljenih obuka'
        return context
    
class TrainingDetailView(LoginRequiredMixin, DetailView):
    model = Training
    template_name = 'staff/training_detail.html'
    context_object_name = 'training'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training = self.get_object()

        context['title'] = 'Detalji o obuci'
        context['staff_list'] = training.staff.all()
        context['method_list'] = training.methods.all()

        return context
class TrainingCreateView(LoginRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('training_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Formiraj obuku'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def form_valid(self, form):
        # Save the form and get the Training instance
        response = super().form_valid(form)
        training = self.object

        # Now create StaffMethodTraining records
        methods = training.methods.all()
        staff_members = training.staff.all()

        if methods.exists() and staff_members.exists():
            for staff in staff_members:
                for method in methods:
                    StaffMethodTraining.objects.get_or_create(
                        staff=staff, method=method, training=training
                    )

        # Redirect to the success URL after creating the records
        return response
    
class TrainingUpdateView(LoginRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('training_list')
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmeni obuku'
        context['submit_button_label'] = 'Potvrdi'
        return context

class TrainingTestUpdateView(UpdateView):
    model = TrainingTests
    form_class = TrainingTestForm
    template_name = 'generic_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj PDF test'
        context['submit_button_label'] = 'Sačuvaj'
        return context
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('training_list')
    
class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = Training
    template_name = 'staff/training_confirm_delete.html'
    success_url = reverse_lazy('training_list')

    def get_object(self, queryset=None):
        obj = Training.objects.get(id=self.kwargs.get('pk'))
        return obj

# Views for AuthorizationType
class AuthorizationTypeListView(LoginRequiredMixin, ListView):
    model = AuthorizationType
    template_name = 'staff/authorization_type_list.html'
    context_object_name = 'authorization_types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak tipova ovlašćenja u laboratorijama'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
class AuthorizationTypeCreateView(LoginRequiredMixin, CreateView):
    model = AuthorizationType
    form_class = AuthorizationTypeForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('authorization_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj novi tip ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
class AuthorizationTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AuthorizationType
    form_class = AuthorizationTypeForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('authorization_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi tip ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
class AuthorizationTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AuthorizationType
    template_name = 'staff/authorization_type_confirm_delete.html'
    success_url = reverse_lazy('authorization_type_list')

    def get_object(self, queryset=None):
        obj = AuthorizationType.objects.get(id=self.kwargs.get('pk'))
        return obj

# Views for Authorization
@method_decorator(never_cache, name='dispatch')
class AuthorizationListView(LoginRequiredMixin, ListView):
    model = Authorization
    template_name = 'staff/authorization_list.html'
    context_object_name = 'authorizations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ovlašćenja'
        return context
    
class AuthorizationCreateView(LoginRequiredMixin, FormView):
    form_class = AuthorizationForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('authorization_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Formiraj ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        staff_members = form.cleaned_data['staff']  # This is a queryset of Staff instances
        methods = form.cleaned_data['methods']
        authorization_types = form.cleaned_data['authorization_type']
        date = form.cleaned_data['date']

        # Create Authorization records for each combination of staff, method, and authorization type
        for staff in staff_members:  # Ensure you're iterating over the queryset
            for method in methods:
                for auth_type in authorization_types:
                    try:
                        # Create or get an Authorization instance for each staff-method-auth type combination
                        Authorization.objects.create(
                            staff=staff,  # Single staff instance, not the whole queryset
                            method=method,
                            authorization_type=auth_type,
                            date=date
                        )
                    except IntegrityError:
                        # Handle duplicates if necessary
                        continue

        return super().form_valid(form)


class AuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Authorization
    form_class = AuthorizationUpdateForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('authorization_list')
    
class AuthorizationDeleteView(LoginRequiredMixin, DeleteView):
    model = Authorization

    def get_object(self, queryset=None):
        obj = Authorization.objects.get(id=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('authorization_list')
    
# List View
class NoMethodAuthorizationListView(ListView):
    model = NoMethodAuthorization
    template_name = 'staff/authorization_list_nomethod.html'
    context_object_name = 'authorizations'

# Create View
class NoMethodAuthorizationCreateView(CreateView):
    model = NoMethodAuthorization
    form_class = NoMethodAuthorizationForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('no_method_authorization_list')

# Update View
class NoMethodAuthorizationUpdateView(UpdateView):
    model = NoMethodAuthorization
    form_class = NoMethodAuthorizationForm
    template_name = 'no_method_authorization_form.html'
    success_url = reverse_lazy('no_method_authorization_list')

# Delete View
class NoMethodAuthorizationDeleteView(DeleteView):
    model = NoMethodAuthorization
    template_name = 'no_method_authorization_confirm_delete.html'
    success_url = reverse_lazy('no_method_authorization_list')