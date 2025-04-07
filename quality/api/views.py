from rest_framework import viewsets
from core.models import Center, OrganizationalUnit, Laboratory, CustomUser
from .serializers import CenterSerializer, OrganizationalUnitSerializer, LaboratorySerializer, UserSerializer

class CenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Center.objects.all()
    serializer_class = CenterSerializer

class OrganizationalUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrganizationalUnit.objects.select_related('center').all()
    serializer_class = OrganizationalUnitSerializer

class LaboratoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Laboratory.objects.select_related('organizational_unit', 'organizational_unit__center').all()
    serializer_class = LaboratorySerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.select_related('laboratory').prefetch_related('laboratory_permissions').all()
    serializer_class = UserSerializer
