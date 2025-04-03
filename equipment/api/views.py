from rest_framework import viewsets
from equipment.models import Equipment
from equipment.api.serializers import EquipmentSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
