from rest_framework import viewsets
from equipment.models import Equipment
from equipment.api.serializers import EquipmentSerializer
from equipment.services import get_user_laboratory_equipment
from django_filters.rest_framework import DjangoFilterBackend
from equipment.filters import EquipmentFilter  # gde ti se već nalazifrom rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated

class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EquipmentFilter
    permission_classes = [IsAuthenticated]  # OVO MORA DA POSTOJI

    def get_queryset(self):
        return get_user_laboratory_equipment()
