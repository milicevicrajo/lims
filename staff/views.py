from datetime import date
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from staff.services import get_active_staff_queryset, get_staff_detail_context, get_staff_object
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
from .services import (
    get_job_position_object,
    get_job_position_context,
    get_staff_job_position_initial,
    get_staff_job_position_success_url
)
from .services import (
    get_professional_experience_object,
    get_professional_experience_initial,
    get_professional_experience_success_url,
    get_training_course_object,
    get_training_course_initial,
    get_training_course_success_url,
    get_membership_object,
    get_membership_initial,
    get_membership_success_url
)
from .services import get_staff_job_position_object, get_staff_job_position_success_url
from .services import (
    get_training_object,
    create_staff_method_trainings,
    get_training_success_url,
    get_training_test_success_url,
)
from .services import (
    get_authorization_type_object,
    get_authorization_type_success_url,
)
from .services import (
    create_authorizations,
    get_authorization_object,
    get_authorization_success_url,
)
from .services import (
    get_no_method_authorization_object,
    get_no_method_authorization_success_url,
)

@method_decorator(never_cache, name='dispatch')
class StaffListView(LaboratoryPermissionMixin, ListView):
    model = Staff
    template_name = 'staff/staff_list.html'

    def get_queryset(self):
        return get_active_staff_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak osoblja'
        return context


class StaffCreateView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'submit_button_label': 'Potvrdi',
            'title': 'Dodaj novog zaposlenog',
        })
        return context


class StaffDetailView(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = 'staff/staff_detail.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalji o osoblju'
        context.update(get_staff_detail_context(context['staff']))
        return context


class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Ispravi karton osoblja',
            'submit_button_label': 'Potvrdi',
        })
        return context

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.id})


class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy('staff_list')

    def get_object(self, queryset=None):
        return get_staff_object(self.kwargs.get('pk'))

# Views for JobPosition
class JobPositionListView(LoginRequiredMixin, FilterView):
    model = JobPosition
    template_name = 'staff/job_position_list.html'
    context_object_name = 'job_positions'
    filterset_class = JobTypeFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_job_position_context())
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
        context.update({
            'title': 'Dodaj novu poziciju/radno mesto',
            'submit_button_label': 'Potvrdi'
        })
        return context


class JobPositionUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'staff/job_position_form.html'
    success_url = reverse_lazy('job_position_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Ispravi poziciju/radno mesto',
            'submit_button_label': 'Potvrdi'
        })
        return context


class JobPositionDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPosition
    template_name = 'ims/job_position/job_position_confirm_delete.html'
    success_url = reverse_lazy('job_position_list')

    def get_object(self, queryset=None):
        return get_job_position_object(self.kwargs.get('pk'))


# Staff Job Position views

class StaffJobPositionListView(ListView):
    model = StaffJobPosition
    template_name = 'staff/staffjobposition_list.html'
    context_object_name = 'positions'


class StaffJobPositionCreateView(CreateView):
    model = StaffJobPosition
    form_class = StaffJobPositionForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('staffjobposition_list')

    def get_initial(self):
        initial = super().get_initial()
        initial.update(get_staff_job_position_initial(self.kwargs))
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Dodeli radno mesto osoblju',
            'submit_button_label': 'Potvrdi'
        })
        return context

    def get_success_url(self):
        return get_staff_job_position_success_url(self.object)

# Update an existing job position for staff


class StaffJobPositionUpdateView(UpdateView):
    model = StaffJobPosition
    form_class = StaffJobPositionForm
    template_name = 'ims/generic_form.html'

    def get_success_url(self):
        return get_staff_job_position_success_url(self.object)


class StaffJobPositionDeleteView(DeleteView):
    model = StaffJobPosition

    def get_object(self, queryset=None):
        return get_staff_job_position_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_staff_job_position_success_url(self.object)



# Views for ProfessionalExperience
class ProfessionalExperienceListView(LoginRequiredMixin, ListView):
    model = ProfessionalExperience
    template_name = 'staff/professional_experience_list.html'
    context_object_name = 'professional_experiences'


class ProfessionalExperienceCreateView(LoginRequiredMixin, CreateView):
    model = ProfessionalExperience
    form_class = ProfessionalExperienceForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Dodaj profesionalno iskustvo', 'submit_button_label': 'Potvrdi'})
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial.update(get_professional_experience_initial(self.kwargs))
        return initial

    def get_success_url(self):
        return get_professional_experience_success_url(self.object)


class ProfessionalExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfessionalExperience
    form_class = ProfessionalExperienceForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Ispravi profesionalno iskustvo', 'submit_button_label': 'Potvrdi'})
        return context

    def get_success_url(self):
        return get_professional_experience_success_url(self.object)


class ProfessionalExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = ProfessionalExperience

    def get_object(self, queryset=None):
        return get_professional_experience_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_professional_experience_success_url(self.object)
    

# Views for TrainingCourse
class TrainingCourseListView(LoginRequiredMixin, ListView):
    model = TrainingCourse
    template_name = 'staff/training_course_list.html'
    context_object_name = 'training_courses'


class TrainingCourseCreateView(LoginRequiredMixin, CreateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Dodaj obuku/usavršavanje', 'submit_button_label': 'Potvrdi'})
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial.update(get_training_course_initial(self.kwargs))
        return initial

    def get_success_url(self):
        return get_training_course_success_url(self.object)


class TrainingCourseUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Ispravi obuku/usavršavanje', 'submit_button_label': 'Potvrdi'})
        return context

    def get_success_url(self):
        return get_training_course_success_url(self.object)


class TrainingCourseDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingCourse

    def get_object(self, queryset=None):
        return get_training_course_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_training_course_success_url(self.object)

    
# Views for MembershipInInternationalOrg
class MembershipInInternationalOrgListView(LoginRequiredMixin, ListView):
    model = MembershipInInternationalOrg
    template_name = 'staff/membership_international_org_list.html'
    context_object_name = 'memberships'


class MembershipInInternationalOrgCreateView(LoginRequiredMixin, CreateView):
    model = MembershipInInternationalOrg
    form_class = MembershipInInternationalOrgForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Dodaj članstvo u organizaciji', 'submit_button_label': 'Potvrdi'})
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial.update(get_membership_initial(self.kwargs))
        return initial

    def get_success_url(self):
        return get_membership_success_url(self.object)


class MembershipInInternationalOrgUpdateView(LoginRequiredMixin, UpdateView):
    model = MembershipInInternationalOrg
    form_class = MembershipInInternationalOrgForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Ispravi članstvo u organizaciji', 'submit_button_label': 'Potvrdi'})
        return context

    def get_success_url(self):
        return get_membership_success_url(self.object)


class MembershipInInternationalOrgDeleteView(LoginRequiredMixin, DeleteView):
    model = MembershipInInternationalOrg

    def get_object(self, queryset=None):
        return get_membership_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_membership_success_url(self.object)

    
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
        response = super().form_valid(form)
        create_staff_method_trainings(self.object)
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
        return get_training_test_success_url(self.request)
    
class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = Training
    template_name = 'staff/training_confirm_delete.html'
    success_url = reverse_lazy('training_list')

    def get_object(self, queryset=None):
        return get_training_object(self.kwargs.get('pk'))

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
    success_url = get_authorization_type_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj novi tip ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context


class AuthorizationTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AuthorizationType
    form_class = AuthorizationTypeForm
    template_name = 'generic_form.html'
    success_url = get_authorization_type_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi tip ovlašćenja'
        context['submit_button_label'] = 'Potvrdi'
        return context


class AuthorizationTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AuthorizationType
    template_name = 'staff/authorization_type_confirm_delete.html'
    success_url = get_authorization_type_success_url()

    def get_object(self, queryset=None):
        return get_authorization_type_object(self.kwargs.get('pk'))


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
        staff_members = form.cleaned_data['staff']
        methods = form.cleaned_data['methods']
        authorization_types = form.cleaned_data['authorization_type']
        date = form.cleaned_data['date']

        create_authorizations(staff_members, methods, authorization_types, date)

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
        return get_authorization_success_url(self.request)


class AuthorizationDeleteView(LoginRequiredMixin, DeleteView):
    model = Authorization

    def get_object(self, queryset=None):
        return get_authorization_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_authorization_success_url(self.request)

# Views for NoMethodAuthorization
class NoMethodAuthorizationListView(LoginRequiredMixin, ListView):
    model = NoMethodAuthorization
    template_name = 'staff/authorization_list_nomethod.html'
    context_object_name = 'authorizations'


class NoMethodAuthorizationCreateView(LoginRequiredMixin, CreateView):
    model = NoMethodAuthorization
    form_class = NoMethodAuthorizationForm
    template_name = 'generic_form.html'

    def get_success_url(self):
        return get_no_method_authorization_success_url(self.request)


class NoMethodAuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = NoMethodAuthorization
    form_class = NoMethodAuthorizationForm
    template_name = 'generic_form.html'

    def get_success_url(self):
        return get_no_method_authorization_success_url(self.request)


class NoMethodAuthorizationDeleteView(LoginRequiredMixin, DeleteView):
    model = NoMethodAuthorization
    template_name = 'generic_form.html'

    def get_object(self, queryset=None):
        return get_no_method_authorization_object(self.kwargs.get('pk'))

    def get_success_url(self):
        return get_no_method_authorization_success_url(self.request)
