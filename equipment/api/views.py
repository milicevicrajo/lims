from jsonschema import ValidationError
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from equipment.models import Equipment, Calibration, InternalControl, Repair
from .serializers import (
    EquipmentSerializer,
    CalibrationSerializer,
    InternalControlSerializer,
    RepairSerializer,
)
from equipment.services import (
    get_rashodovana_oprema_for_user,
    get_user_laboratory_equipment,
    get_user_equipment_queryset,
    calculate_equipment_calibration_scores,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from equipment.models import Equipment
from .serializers import EquipmentSerializer
from equipment.services import (
    get_user_equipment_queryset,
    get_rashodovana_oprema_for_user,
    create_equipment,
    update_equipment,
    toggle_equipment_status,
    update_pomocna_equipment,
    get_user_laboratory_equipment,
    calculate_equipment_calibration_scores,
    get_internal_controls_with_devices,
    annotate_next_calibration_date,
    generate_equipment_qr_data,
    get_latest_calibrations_for_user,
    create_calibration,
    update_calibration,
    create_internal_control,
    add_controlling_device,
    remove_controlling_device,
    create_repair,
    update_repair
)
from rest_framework import viewsets, status
from django.http import HttpResponse


@extend_schema(tags=['Equipment'])
class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer

    def get_queryset(self):
        user = self.request.user
        # Po defaultu - aktivna oprema
        return get_user_equipment_queryset(user)

    def perform_create(self, serializer):
        equipment = create_equipment(serializer.validated_data, self.request.user)
        serializer.instance = equipment

    def retrieve(self, request, *args, **kwargs):
        equipment = self.get_object()

        # Standardni serializer output
        equipment_data = EquipmentSerializer(equipment, context={'request': request}).data

        # Dodaj dodatne podatke iz MVT context-a
        equipment_data.update(calculate_equipment_calibration_scores(equipment) or {})

        # Najnovije etaloniranje
        latest_calibration = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date').first()
        equipment_data['latest_calibration'] = CalibrationSerializer(latest_calibration, context={'request': request}).data if latest_calibration else None

        # Najnovija interna kontrola
        equipment_data['latest_internal_controls'] = [
            {
                'internal_control': internal_control['internal_control'].id,  # možeš detaljnije ako hoćeš serializer
                'controlling_devices': [device.id for device in internal_control['controlling_devices']]
            }
            for internal_control in get_internal_controls_with_devices(equipment)
        ]

        # Najnovija popravka
        latest_repair = Repair.objects.filter(equipment=equipment).order_by('-malfunction_date').first()
        equipment_data['latest_repair'] = RepairSerializer(latest_repair, context={'request': request}).data if latest_repair else None

        # Pomoćna oprema
        pomocna_equipments = Equipment.objects.filter(main_equipment=equipment, equipment_type='Pomocna')
        equipment_data['pomocna_equipments'] = EquipmentSerializer(pomocna_equipments, many=True, context={'request': request}).data

        # Sva kalibracija
        all_calibrations = Calibration.objects.filter(equipment=equipment).order_by('-calibration_date')
        equipment_data['all_calibrations'] = CalibrationSerializer(all_calibrations, many=True, context={'request': request}).data

        return Response(equipment_data)

    def perform_update(self, serializer):
        update_equipment(self.get_object(), serializer)

    def perform_destroy(self, instance):
        instance.delete()

    # ✅ Custom akcija: Rashodovana oprema
    @action(detail=False, methods=['get'])
    def rashodovana(self, request):
        queryset = get_rashodovana_oprema_for_user(request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ✅ Custom akcija: Promeni status rashodovanja
    @action(detail=True, methods=['post'])
    def toggle_rashodovana(self, request, pk=None):
        equipment = self.get_object()
        equipment = toggle_equipment_status(equipment)
        return Response({
            'status': 'Rashodovana status promenjen',
            'is_rashodovana': equipment.is_rashodovana
        })

    # ✅ Custom akcija: Pomoćna oprema dodavanje/uklanjanje
    @action(detail=True, methods=['post'])
    def pomocna_oprema(self, request, pk=None):
        main_equipment = self.get_object()
        selected_equipment_id = request.data.get('equipment_id')
        action_type = request.data.get('action')

        if not selected_equipment_id or not action_type:
            return Response({'error': 'equipment_id i action su obavezni.'}, status=status.HTTP_400_BAD_REQUEST)

        response = update_pomocna_equipment(main_equipment, selected_equipment_id, action_type)
        return Response(response)

    @action(detail=True, methods=['get'], url_path='qr-code')
    def qr_code(self, request, pk=None):
        equipment = self.get_object()
        qr_image = generate_equipment_qr_data(equipment, request)
        return HttpResponse(qr_image, content_type="image/png")


@extend_schema(tags=['Calibration'])
class CalibrationViewSet(viewsets.ModelViewSet):
    serializer_class = CalibrationSerializer

    def get_queryset(self):
        return get_latest_calibrations_for_user(self.request.user)

    def perform_create(self, serializer):
        try:
            calibration = create_calibration(serializer.validated_data, self.request.user)
            serializer.instance = calibration
        except ValidationError as e:
            raise ValidationError({'detail': str(e)})

    def perform_update(self, serializer):
        try:
            update_calibration(self.get_object(), serializer.validated_data, self.request.user)
        except ValidationError as e:
            raise ValidationError({'detail': str(e)})

    def perform_destroy(self, instance):
        instance.delete()


@extend_schema(tags=['Internal Control'])
class InternalControlViewSet(viewsets.ModelViewSet):
    queryset = InternalControl.objects.all()
    serializer_class = InternalControlSerializer

    def create(self, request, *args, **kwargs):
        try:
            internal_control = create_internal_control(request.data, request.user)
            serializer = self.get_serializer(internal_control)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        try:
            updated_control = update_internal_control(instance, request.data, request.user)
            serializer = self.get_serializer(updated_control, partial=partial)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def controlling_devices(self, request, pk=None):
        internal_control = self.get_object()
        action_type = request.data.get('action')
        equipment_id = request.data.get('equipment_id')

        if not equipment_id:
            return Response({'message': 'Equipment ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        equipment = get_object_or_404(Equipment, id=equipment_id)

        if action_type == 'add':
            message = add_controlling_device(internal_control, equipment)
        elif action_type == 'remove':
            message = remove_controlling_device(internal_control, equipment)
        else:
            return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': message, 'equipment_id': equipment_id, 'action': action_type}, status=status.HTTP_200_OK)


@extend_schema(tags=['Repair'])
class RepairViewSet(viewsets.ModelViewSet):
    queryset = Repair.objects.all()
    serializer_class = RepairSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Repair.objects.all()
        return Repair.objects.filter(equipment__responsible_laboratory__in=user.laboratory_permissions.all())

    def create(self, request, *args, **kwargs):
        try:
            repair = create_repair(request.data, request.user)
            serializer = self.get_serializer(repair)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_repair = update_repair(instance, request.data, request.user)
            serializer = self.get_serializer(updated_repair)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


