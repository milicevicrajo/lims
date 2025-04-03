from .models import * 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery, F
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django_filters.views import FilterView
from .filters import EquipmentFilter, UserLabEquipmentFilter
from .forms import EquipmentForm, CalibrationForm, InternalControlForm, RepairForm
from lims.mixins import LaboratoryRoleMixin
import qrcode
from django.http import HttpResponse
import io

# EQUIPMENT
@method_decorator(never_cache, name='dispatch')
class EquipmentListView(LoginRequiredMixin, FilterView):
    model = Equipment
    filterset_class = EquipmentFilter
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter the queryset to include only non-rashodovana equipment
        queryset = queryset.filter(is_rashodovana=False)
        # Annotate the queryset with the next calibration date
        next_calibration_date_subquery = Calibration.objects.filter(
            equipment_id=OuterRef('pk')
        ).order_by('-calibration_date').values('next_calibration_date')[:1]
        queryset = queryset.annotate(next_calibration_date=Subquery(next_calibration_date_subquery))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kompletan spisak opreme u svim laboratorijama'
        return context
    


@method_decorator(never_cache, name='dispatch')
class UserLabEquipmentListView(LoginRequiredMixin, FilterView):
    model = Equipment
    filterset_class = UserLabEquipmentFilter
    template_name = 'equipment/equipment_list.html'  # Update as needed
    context_object_name = 'equipments'
    
    def get_filterset(self, filterset_class):
        # Check if 'equipment_type' is in the request and not set to an empty string
        if 'equipment_type' not in self.request.GET:
            # Copy the GET parameters to modify them
            data = self.request.GET.copy()
            # Ensure 'equipment_type' is set to 'Glavna' if not provided and not explicitly set to ''
            data['equipment_type'] = 'Glavna'
            return filterset_class(data, queryset=self.get_queryset())
        else:
            return filterset_class(self.request.GET, queryset=self.get_queryset())

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter equipment to only include those in the user's laboratory
        if self.request.user.is_authenticated and self.request.user.laboratory:
            queryset = queryset.filter(responsible_laboratory=self.request.user.laboratory, is_rashodovana=False)
        else:
            # If the user doesn't belong to any laboratory, return an empty queryset
            queryset = Equipment.objects.none()

        # Annotate the queryset with the next calibration date
        next_calibration_date_subquery = Calibration.objects.filter(
            equipment_id=OuterRef('pk')  # Assuming 'pk' is the primary key of Equipment
        ).order_by('-calibration_date').values('next_calibration_date')[:1]

        queryset = queryset.annotate(next_calibration_date=Subquery(next_calibration_date_subquery))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak opreme u mojoj laboratoriji' 
        return context


@method_decorator(never_cache, name='dispatch')
class RashodovanaEquipmentListView(LoginRequiredMixin, FilterView):
    model = Equipment
    filterset_class = UserLabEquipmentFilter
    template_name = 'equipment/equipment_list.html'  # Update as needed
    context_object_name = 'equipments'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter equipment to only include those in the user's laboratory
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
            responsible_laboratory__in=self.request.user.laboratory_permissions.all(), 
            is_rashodovana=True
        )
        else:
            # If the user doesn't belong to any laboratory, return an empty queryset
            queryset = Equipment.objects.none()

        # Annotate the queryset with the next calibration date
        next_calibration_date_subquery = Calibration.objects.filter(
            equipment_id=OuterRef('pk')  # Assuming 'pk' is the primary key of Equipment
        ).order_by('-calibration_date').values('next_calibration_date')[:1]

        queryset = queryset.annotate(next_calibration_date=Subquery(next_calibration_date_subquery))

        return queryset

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
        # Check if user is authenticated and not None
        if self.request.user and self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                form.instance.responsible_laboratory = self.request.user.laboratory
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            print('ERROR>>>>>>', e)
            form.add_error('card_number', 'Broj kartona već postoji.')
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
        # download_url = reverse('download_populated_document') + f"?card_number={equipment.card_number}"
        # Get all fields from the Equipment model, filtering out fields starting with an underscore

        # Fetch the latest calibration
        latest_calibration = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date').first()
        
        # Calculate the calibration interval and scores if there is a calibration record
        if latest_calibration:
            selected_interval, calculated_interval, ocena1, ocena2, ocena3, ocena4, ocena5 = latest_calibration.calculate_calibration_interval()
            context['selected_interval'] = selected_interval
            context['calculated_interval'] = calculated_interval
            context['ocena1'] = round(ocena1*0.2,3)
            context['ocena2'] = round(ocena2*0.2,3)
            context['ocena3'] = round(ocena3*0.1,3)
            context['ocena4'] = round(ocena4*0.3,3)
            context['ocena5'] = round(ocena5*0.2,3)
            context['korekcioni_faktor'] = round((ocena1*0.2+ocena2*0.2+ocena3*0.1+ocena4*0.3+ocena5*0.2),2)
        else:
            context['selected_interval'] = None
            context['calculated_interval'] = None
            context['ocena1'] = None
            context['ocena2'] = None
            context['ocena3'] = None
            context['ocena4'] = None
            context['ocena5'] = None
            context['korekcioni_faktor'] = None

        # Fetch the latest 5 internal controls and their controlling devices
        latest_internal_controls = InternalControl.objects.filter(equipment=equipment).order_by('-last_control_date')[:5]
        internal_controls_with_devices = [
            {
                'internal_control': internal_control,
                'controlling_devices': internal_control.controlling_devices.all()
            }
            for internal_control in latest_internal_controls
        ]

        context['latest_calibration'] = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date').first()
        context['latest_internal_controls'] = internal_controls_with_devices
        context['latest_repair'] = Repair.objects.filter(equipment=equipment).order_by('-malfunction_date').first()
        context['pomocna_equipments'] = Equipment.objects.filter(main_equipment=equipment, equipment_type='Pomocna')
        # context['download_url'] = download_url
        context['all_calibrations'] = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date')

        return context

def generate_qr_code(request, equipment_id):
    # Dobavi opremu iz baze
    equipment = get_object_or_404(Equipment, id=equipment_id)

    # Definiši URL ili podatke koje želiš da enkodiraš u QR kod
    qr_data = f"{request.build_absolute_uri('/')[:-1]}{equipment.get_absolute_url()}"

    # Generiši QR kod
    qr = qrcode.make(qr_data)

    # Sačuvaj QR kod u memorijski buffer
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    # Pošalji QR kod kao HTTP response
    return HttpResponse(buffer.getvalue(), content_type="image/png")

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
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    
    def get_success_url(self):
        # Define the success URL
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

        if selected_equipment_id:
            selected_equipment = Equipment.objects.get(id=selected_equipment_id)
            if action == 'add':
                selected_equipment.main_equipment = equipment
                selected_equipment.save()
                message = f'Oprema {selected_equipment} dodata u pomoćnu opremu.'
            elif action == 'remove':
                selected_equipment.main_equipment = None
                selected_equipment.save()
                message = f'Oprema {selected_equipment} uklonjena iz pomoćne opreme.'

            return JsonResponse({'message': message, 'equipment_id': selected_equipment_id, 'action': action})

        return JsonResponse({'message': 'Invalid request'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'laboratory') and self.request.user.laboratory and hasattr(self.request.user.laboratory, 'org_unit'):
            org_unit = self.request.user.laboratory.org_unit
            equipment_queryset = Equipment.objects.filter(
                responsible_laboratory__org_unit=org_unit,
                equipment_type='Pomocna',
                is_rashodovana=False,
                main_equipment__isnull=True  # equipment with main_equipment as None
            ) | Equipment.objects.filter(
                responsible_laboratory__org_unit=org_unit,
                equipment_type='Pomocna',
                is_rashodovana=False,
                main_equipment=equipment  # equipment with current equipment as main_equipment
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
        user = self.request.user

        if user.is_authenticated and user.laboratory_permissions.exists():
            # Uzimamo samo opremu iz laboratorija na koje korisnik ima dozvolu
            equipment_ids = Equipment.objects.filter(
                responsible_laboratory__in=user.laboratory_permissions.all()
            ).values_list('id', flat=True)

            # Subquery koji uzima poslednji datum etaloniranja po opremi
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

        return Calibration.objects.none()

class CalibrationCreate(LoginRequiredMixin, CreateView):
    form_class = CalibrationForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('calibration_list')  # Redirect after successful creation

    def get_form_kwargs(self):
        kwargs = super(CalibrationCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Ensure 'user' is passed to form
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj karton o etaloniranju'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.kwargs.get('equipment_id', None)
        if equipment_id:
            initial['equipment'] = Equipment.objects.get(id=equipment_id)
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the user to the current user
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error('certificate_number', 'Broj kartona već postoji.')
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('equipment_detail', kwargs={'pk': self.object.equipment.id})
    
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
    
    def get_success_url(self):
        # Define the success URL
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
        form.instance.user = self.request.user  # Set the user to the current user
        return super().form_valid(form)

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

        if selected_equipment_id:
            try:
                selected_equipment = Equipment.objects.get(id=selected_equipment_id)
                if action == 'add':
                    internal_control.controlling_devices.add(selected_equipment)
                    message = 'Added'
                elif action == 'remove':
                    internal_control.controlling_devices.remove(selected_equipment)
                    message = 'Removed'
                else:
                    message = 'Invalid action'
                
                internal_control.save()
                return JsonResponse({'message': message, 'equipment_id': selected_equipment_id, 'action': action})
            except Equipment.DoesNotExist:
                return JsonResponse({'message': 'Equipment not found'}, status=404)

        return JsonResponse({'message': 'Invalid request'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        internal_control = self.get_object()
        controlling_devices = internal_control.controlling_devices.all()

        if self.request.user.is_authenticated and self.request.user.laboratory_permissions.exists():
            # Uzimamo sve organizacione jedinice iz laboratorija na koje korisnik ima pristup
            org_units = self.request.user.laboratory_permissions.values_list('organizational_unit', flat=True)

            equipment_queryset = Equipment.objects.filter(
                responsible_laboratory__organizational_unit__in=org_units,
                is_rashodovana=False,
            )



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
class RepairsListView(ListView):
    model = Repair
    template_name = 'equipment/repair_l.html'
    context_object_name = 'repair'

    def get_queryset(self):
        return Calibration.objects.select_related('equipment').all()

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
        form.instance.user = self.request.user  # Set the user to the current user
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.equipment.id:
            return reverse('equipment_detail', kwargs={'pk': self.object.equipment.id})
        else:
            return reverse('equipment_list')

class RepairDetail(LoginRequiredMixin, DetailView):
    model = InternalControl
    template_name = 'equipment/repair_detail.html'

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(InternalControl, pk=pk)

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

    def get_success_url(self):
        # Define the success URL
         return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})

class RepairDelete(LaboratoryRoleMixin, LoginRequiredMixin, DeleteView):
    model = Repair
    
    def get_object(self, queryset=None):
        obj = Repair.objects.get(pk=self.kwargs.get('pk'))
        return obj
    
    def get_success_url(self):
        # Define the success URL
         return reverse_lazy('equipment_detail', kwargs={'pk': self.object.equipment.id})