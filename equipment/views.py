from .models import * 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import OuterRef, Subquery, F
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django_filters.views import FilterView
from .filters import EquipmentFilter, UserLabEquipmentFilter
from .forms import EquipmentForm, CalibrationForm, InternalControlForm, RepairForm
from lims.mixins import LaboratoryRoleMixin
from django.http import HttpResponse
from equipment.services import add_controlling_device, annotate_next_calibration_date, create_calibration, create_internal_control, create_repair, generate_equipment_qr_data, calculate_equipment_calibration_scores, get_internal_controls_with_devices, get_latest_calibrations_for_user, get_rashodovana_oprema_for_user, get_user_equipment_queryset, get_user_laboratory_equipment, remove_controlling_device, update_calibration, update_equipment, update_pomocna_equipment, update_repair
from equipment.services import create_equipment

# EQUIPMENT
@method_decorator(never_cache, name='dispatch')
class EquipmentListView(LoginRequiredMixin, FilterView):
    model = Equipment
    filterset_class = UserLabEquipmentFilter
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        return get_user_equipment_queryset(self.request.user)
    
    def get_filterset(self, filterset_class):
        data = self.request.GET.copy()

        if 'equipment_type' not in data:
            data['equipment_type'] = 'Glavna'

        return filterset_class(data, queryset=self.get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kompletan spisak opreme u svim laboratorijama'
        return context

@method_decorator(never_cache, name='dispatch')
class RashodovanaEquipmentListView(LoginRequiredMixin, FilterView):
    model = Equipment
    filterset_class = UserLabEquipmentFilter
    template_name = 'equipment/equipment_list.html'  # Update as needed
    context_object_name = 'equipments'

    def get_queryset(self):
        return get_rashodovana_oprema_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak rashodovane opreme u mojoj laboratoriji'  # Optional: add any additional context
        return context

class EquipmentCreate(LoginRequiredMixin, CreateView):
    form_class = EquipmentForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('equipment_list')  # Redirect after successful creation
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to the form kwargs
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj novi karton opreme'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        print(initial)
        equipment_id = self.kwargs.get('equipment_id', None)
        if equipment_id:
            initial['equipment_type'] = self.request.GET.get('equipment_type', 'Pomocna')
            initial['main_equipment'] = Equipment.objects.get(id=equipment_id)
        return initial
    
    def form_valid(self, form):
        try:
            equipment = create_equipment(form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=equipment.pk)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        
@method_decorator(never_cache, name='dispatch')
class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs['user'] = self.request.user
        equipment = context['equipment']

        context.update(calculate_equipment_calibration_scores(equipment) or {})
        context['latest_calibration'] = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date').first()
        context['latest_internal_controls'] = get_internal_controls_with_devices(equipment)
        context['latest_repair'] = Repair.objects.filter(equipment=equipment).order_by('-malfunction_date').first()
        context['pomocna_equipments'] = Equipment.objects.filter(main_equipment=equipment, equipment_type='Pomocna')
        # context['download_url'] = download_url
        context['all_calibrations'] = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date')

        return context

def generate_qr_code(request, equipment_id):
    # Dobavi opremu iz baze
    equipment = get_object_or_404(Equipment, id=equipment_id)

    return HttpResponse(generate_equipment_qr_data(equipment, request), content_type="image/png")


class EquipmentUpdate(LaboratoryRoleMixin, LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'generic_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi karton opreme'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        update_equipment(self.object, form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.id})
    
class SelectPomocnaEquipmentView(DetailView):
    model = Equipment
    filterset_class = EquipmentFilter
    template_name = 'equipment/select_equipment_pomocna.html'
    context_object_name = 'equipment'

    def post(self, request, *args, **kwargs):
        equipment = self.get_object()
        action = request.POST.get('action')
        selected_equipment_id = request.POST.get('equipment_id')

        if selected_equipment_id and action:
            response = update_pomocna_equipment(equipment, selected_equipment_id, action)
            if response['success']:
                return JsonResponse(response)
            else:
                return JsonResponse(response, status=400)

        return JsonResponse({'message': 'Invalid request'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()

        # Ovo možeš dodatno da prebaciš u service ako želiš (predlog)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'laboratory') and self.request.user.laboratory and hasattr(self.request.user.laboratory, 'org_unit'):
            org_unit = self.request.user.laboratory.org_unit
            equipment_queryset = Equipment.objects.filter(
                responsible_laboratory__org_unit=org_unit,
                equipment_type='Pomocna',
                is_rashodovana=False,
                main_equipment__isnull=True
            ) | Equipment.objects.filter(
                responsible_laboratory__org_unit=org_unit,
                equipment_type='Pomocna',
                is_rashodovana=False,
                main_equipment=equipment
            )
        else:
            equipment_queryset = Equipment.objects.filter(equipment_type='Pomocna')

        equipment_filter = EquipmentFilter(self.request.GET, queryset=equipment_queryset)
        context['filter'] = equipment_filter
        context['all_equipment'] = equipment_filter.qs
        return context



class EquipmentDelete(LaboratoryRoleMixin, LoginRequiredMixin, DeleteView):
    model = Equipment
    success_url = reverse_lazy('equipment_list')  # Redirect to the equipment list after deletion

    def get_object(self, queryset=None):
        obj = Equipment.objects.get(id=self.kwargs.get('pk'))
        return obj
    
@login_required
@require_POST
def change_rashodovana_status(request, equipment_id):
    """
    Toggle the `is_rashodovana` status of a piece of equipment.
    """
    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.is_rashodovana = not equipment.is_rashodovana
    equipment.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Oprema {equipment.card_number}> is_rashodovana status je promenjen {equipment.is_rashodovana}.'
    })

# CALIBRATIONS 
class CalibrationListView(LoginRequiredMixin, ListView):
    model = Calibration
    template_name = 'equipment/calibration_list.html'
    context_object_name = 'calibrations'

    def get_queryset(self):
        return get_latest_calibrations_for_user(self.request.user)

class CalibrationCreate(LoginRequiredMixin, CreateView):
    form_class = CalibrationForm
    template_name = 'generic_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj karton o etaloniranju'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.kwargs.get('equipment_id')
        if equipment_id:
            initial['equipment'] = Equipment.objects.get(id=equipment_id)
        return initial

    def form_valid(self, form):
        try:
            calibration = create_calibration(form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=calibration.equipment.id)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
    
@method_decorator(never_cache, name='dispatch')
class CalibrationDetail(LoginRequiredMixin, DetailView):
    model = Calibration
    template_name = 'equipment/calibration_detail.html'

class CalibrationUpdate(LaboratoryRoleMixin, LoginRequiredMixin, UpdateView):
    model = Calibration
    form_class = CalibrationForm
    template_name = 'generic_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi karton etaloniranja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            calibration = update_calibration(self.object, form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=calibration.equipment.id)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})


class CalibrationDelete(LaboratoryRoleMixin, LoginRequiredMixin, DeleteView):
    model = Calibration
    def get_object(self, queryset=None):
        obj = Calibration.objects.get(id=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})

# INTERNAL CONTROL
class InternalControlListView(LoginRequiredMixin, ListView):
    model = InternalControl
    template_name = 'equipment/internal_control_list.html'
    context_object_name = 'internal_control'

    def get_queryset(self):
        return Calibration.objects.select_related('equipment').all()

class InternalControlCreate(LoginRequiredMixin, CreateView):
    form_class = InternalControlForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj zapis o internoj kontroli'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.kwargs.get('equipment_id', None)
        if equipment_id:
            initial['equipment'] = Equipment.objects.get(id=equipment_id)
        return initial

    def form_valid(self, form):
        try:
            internal_control = create_internal_control(form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=internal_control.equipment.id)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('equipment_detail', kwargs={'pk': self.object.equipment.id})

    
class SelectControllingDevicesView(DetailView):
    model = InternalControl
    filterset_class = EquipmentFilter
    template_name = 'equipment/select_equipment_interna.html'
    context_object_name = 'internal_control'

    def post(self, request, *args, **kwargs):
        internal_control = self.get_object()
        action = request.POST.get('action')
        selected_equipment_id = request.POST.get('equipment_id')

        if not selected_equipment_id:
            return JsonResponse({'message': 'Invalid request'}, status=400)

        try:
            selected_equipment = Equipment.objects.get(id=selected_equipment_id)
        except Equipment.DoesNotExist:
            return JsonResponse({'message': 'Equipment not found'}, status=404)

        if action == 'add':
            message = add_controlling_device(internal_control, selected_equipment)
        elif action == 'remove':
            message = remove_controlling_device(internal_control, selected_equipment)
        else:
            message = 'Invalid action'
            return JsonResponse({'message': message}, status=400)

        return JsonResponse({'message': message, 'equipment_id': selected_equipment_id, 'action': action})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        internal_control = self.get_object()
        controlling_devices = internal_control.controlling_devices.all()

        equipment_queryset = get_user_equipment_queryset(self.request.user)

        equipment_filter = EquipmentFilter(self.request.GET, queryset=equipment_queryset)
        context['filter'] = equipment_filter
        context['all_equipment'] = equipment_filter.qs
        context['latest_internal_control'] = internal_control
        context['controlling_devices_ids'] = [device.id for device in controlling_devices]
        return context

    
class InternalControlDetail(DetailView):
    model = InternalControl
    template_name = 'equipment/internal_control_detail.html'

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(InternalControl, pk=pk)

class InternalControlUpdate(LaboratoryRoleMixin, LoginRequiredMixin, UpdateView):
    model = InternalControl
    form_class = InternalControlForm
    template_name = '/generic_form.html'

    def get_form_kwargs(self):        
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi internu kontrolu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(InternalControl, pk=pk)

    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})

class InternalControlDelete(LaboratoryRoleMixin, LoginRequiredMixin, DeleteView):
    model = InternalControl
    
    def get_object(self, queryset=None):
        obj = InternalControl.objects.get(pk=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        # Define the success URL
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})


# REPAIRS

class RepairCreate(LoginRequiredMixin, CreateView):
    form_class = RepairForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj zapis o popravci'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.kwargs.get('equipment_id', None)
        if equipment_id:
            initial['equipment'] = Equipment.objects.get(id=equipment_id)
        return initial

    def form_valid(self, form):
        try:
            repair = create_repair(form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=repair.equipment.id)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('equipment_list')
class RepairDetail(LoginRequiredMixin, DetailView):
    model = Repair
    template_name = 'equipment/repair_detail.html'

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Repair, pk=pk)

class RepairUpdate(LaboratoryRoleMixin, LoginRequiredMixin, UpdateView):
    model = Repair
    form_class = RepairForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi zapis o popravci'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Repair, pk=pk)

    def form_valid(self, form):
        try:
            update_repair(self.get_object(), form.cleaned_data, self.request.user)
            return redirect('equipment_detail', pk=self.object.equipment.id)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})

class RepairDelete(LaboratoryRoleMixin, LoginRequiredMixin, DeleteView):
    model = Repair
    
    def get_object(self, queryset=None):
        obj = Repair.objects.get(pk=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        # Define the success URL
         return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})