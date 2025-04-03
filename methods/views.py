from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import Standard, TestingArea, TestSubject, SubDiscipline, Method
from .forms import StandardForm, TestingAreaForm, TestSubjectForm, SubDisciplineForm, MethodForm
from .filters import MethodFilter
from staff.models import Authorization, Training
from quality.models import ControlTestingMethod, PTSchemeMethod, MeasurementUncertainty
from lims.mixins import LaboratoryRoleMixin
from equipment.models import Equipment
from equipment.filters import EquipmentFilter

# STANDARD 
@method_decorator(never_cache, name='dispatch')
class StandardListView(ListView):
    model = Standard
    template_name = 'methods/standard_list.html'
    context_object_name = 'standards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak svih standarda'
        return context

class StandardCreateView(CreateView):
    model = Standard
    form_class = StandardForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('standard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj zapis o standardu'
        context['submit_button_label'] = 'Potvrdi'
        return context

class StandardUpdateView(UpdateView):
    model = Standard
    form_class = StandardForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('standard_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi zapis o standardu'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
class StandardDeleteView(DeleteView):
    model = Standard

    success_url = reverse_lazy('standard_list')  # Redirect to the standard list after deletion

    def get_object(self, queryset=None):
        obj = Standard.objects.get(id=self.kwargs.get('pk'))
        return obj

# TESTING AREA and TEST SUBJECT
class TestingAreaCreateView(LoginRequiredMixin, CreateView):
    model = TestingArea
    form_class = TestingAreaForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('testandarea_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj oblst ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

class TestingAreaUpdateView(LoginRequiredMixin, UpdateView):
    model = TestingArea
    form_class = TestingAreaForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('testandarea_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi oblast ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

class TestingAreaDeleteView(LoginRequiredMixin, DeleteView):
    model = TestingArea
    success_url = reverse_lazy('testandarea_list')
    def get_object(self, queryset=None):
        obj = TestingArea.objects.get(id=self.kwargs.get('pk'))
        return obj

class TestSubjectCreateView(LoginRequiredMixin, CreateView):
    model = TestSubject
    form_class = TestSubjectForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('testandarea_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj predmet ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context
class TestSubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = TestSubject
    form_class = TestSubjectForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('testandarea_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi predmet ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context
class TestSubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = TestSubject
    success_url = reverse_lazy('testandarea_list')

    def get_object(self, queryset=None):
        obj = TestSubject.objects.get(id=self.kwargs.get('pk'))
        return obj

class CombinedListView(LoginRequiredMixin, ListView):
    template_name = 'methods/testing_area_subject_list.html'
    context_object_name = 'data'

    def get_queryset(self):
        return {
            'testing_areas': TestingArea.objects.all(),
            'test_subjects': TestSubject.objects.all()
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testing_areas'] = TestingArea.objects.all()
        context['test_subjects'] = TestSubject.objects.all()
        context['title'] = 'Spisak oblasti i predmeta ispitivanja sa pripadajućim kodovima'
        return context
    
# SUBDISCIPLINE 
@method_decorator(never_cache, name='dispatch')
class SubDisciplineListView(LoginRequiredMixin, ListView):
    model = SubDiscipline
    template_name = 'methods/sub_discipline_list.html'
    context_object_name = 'sub_disciplines'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak poddisciplina'
        return context
    
class SubDisciplineDetailView(DetailView):
    model = SubDiscipline
    template_name = 'methods/sub_discipline_detail.html'
    context_object_name = 'sub_discipline'  # This is the name used in the template to refer to the object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the related methods for this sub_discipline
        context['methods'] = Method.objects.filter(subdiscipline=self.object)
        context['title'] = 'Spisak metoda unutar poddiscipline'
        return context
class SubDisciplineCreateView(LoginRequiredMixin, CreateView):
    model = SubDiscipline
    form_class = SubDisciplineForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('sub_discipline_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj novu poddisciplinu'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
class SubDisciplineUpdateView(LoginRequiredMixin, UpdateView):
    model = SubDiscipline
    form_class = SubDisciplineForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('sub_discipline_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi poddisciplinu'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SubDisciplineDeleteView(LoginRequiredMixin, DeleteView):
    model = SubDiscipline
    success_url = reverse_lazy('sub_discipline_list')

    def get_object(self, queryset=None):
        obj = SubDiscipline.objects.get(id=self.kwargs.get('pk'))
        return obj
    
# METHOD VIEWS
@method_decorator(never_cache, name='dispatch')
class MethodListView(FilterView):
    model = Method
    filterset_class = MethodFilter
    template_name = 'methods/method_list.html'
    context_object_name = 'methods'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak metoda'
        return context

class MethodDetailView(DetailView):
    model = Method
    template_name = 'methods/method_detail.html'
    context_object_name = 'method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()
        

        context['equipment_list'] = method.equipment.all()
        context['authorizations'] = Authorization.objects.filter(method=method)
        context['trainings'] = Training.objects.filter(methods__in=[method])
        context['control_tests'] = ControlTestingMethod.objects.filter(method=method)
        context['pt_activity'] = PTSchemeMethod.objects.filter(method=method)
        context['measurement_uncertainty'] = MeasurementUncertainty.objects.filter(method=method)

        # context['standard_secondary'] = Method.standard_secondary.filter(method=method)
        return context
    
class MethodCreateView(CreateView):
    model = Method
    form_class = MethodForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('method_list')
    
    manual = "Polje 'Standard - dodatni' se odnosi na dodatke standardu ili u slučajevima kada se dva identična standarda imaju različite oznake može se ubaciti i drugi standard. "

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to the form kwargs
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Formiraj novu metodu'
        context['submit_button_label'] = 'Potvrdi'
        context['manual'] = self.manual
        return context
    

class MethodUpdateView(LaboratoryRoleMixin, UpdateView):
    model = Method
    form_class = MethodForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('method_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to the form kwargs
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi metodu'
        context['submit_button_label'] = 'Potvrdi'
        return context
class MethodDeleteView(DeleteView):
    model = Method
    template_name = 'methods/method_confirm_delete.html'
    success_url = reverse_lazy('method_list')

class SelectEquipmentView(DetailView):
    model = Method
    template_name = 'methods/select_equipment.html'
    context_object_name = 'method'

    def post(self, request, *args, **kwargs):
        method = self.get_object()
        action = request.POST.get('action')
        selected_equipment_id = request.POST.get('equipment_id')

        if selected_equipment_id:
            selected_equipment = Equipment.objects.get(id=selected_equipment_id)
            if action == 'add':
                method.equipment.add(selected_equipment)
                message = 'Oprema dodata u metodu'
            elif action == 'remove':
                method.equipment.remove(selected_equipment)
                message = 'Oprema uklonjena iz metode'

            return JsonResponse({'message': message, 'equipment_id': selected_equipment_id, 'action': action})

        return JsonResponse({'message': 'Invalid request'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()
        
        if self.request.user.is_authenticated and self.request.user.laboratory_permissions.exists():
            # Uzimamo sve organizacione jedinice iz laboratorija koje korisnik ima pravo da vidi
            org_units = self.request.user.laboratory_permissions.values_list('organizational_unit', flat=True)

            equipment_queryset = Equipment.objects.filter(
                responsible_laboratory__organizational_unit__in=org_units,
                equipment_type='Glavna',
                is_rashodovana=False
            )
        else:
            # Ako korisnik nema laboratorije ili nije prijavljen, prikazujemo sve (ili prazno ako hoćeš da ograničiš)
            equipment_queryset = Equipment.objects.filter(
                equipment_type='Glavna',
                is_rashodovana=False
    )


        equipment_filter = EquipmentFilter(self.request.GET, queryset=equipment_queryset)
        context['filter'] = equipment_filter
        context['all_equipment'] = equipment_filter.qs
        return context