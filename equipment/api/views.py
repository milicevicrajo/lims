from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from equipment.models import Equipment, Calibration, InternalControl, Repair
from .serializers import (
    EquipmentSerializer,
    CalibrationSerializer,
    InternalControlSerializer,
    RepairSerializer,
)

@extend_schema(tags=['Equipment'])
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

@extend_schema(tags=['Calibration'])
class CalibrationViewSet(viewsets.ModelViewSet):
    queryset = Calibration.objects.all()
    serializer_class = CalibrationSerializer

@extend_schema(tags=['Internal Control'])
class InternalControlViewSet(viewsets.ModelViewSet):
    queryset = InternalControl.objects.all()
    serializer_class = InternalControlSerializer

@extend_schema(tags=['Repair'])
class RepairViewSet(viewsets.ModelViewSet):
    queryset = Repair.objects.all()
    serializer_class = RepairSerializer


