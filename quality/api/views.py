from rest_framework import viewsets
from quality.models import (
    PTScheme,
    PTSchemeMethod,
    ControlTesting,
    ControlTestingMethod,
    MeasurementUncertainty
)
from .serializers import (
    PTSchemeSerializer,
    PTSchemeMethodSerializer,
    ControlTestingSerializer,
    ControlTestingMethodSerializer,
    MeasurementUncertaintySerializer
)

class PTSchemeViewSet(viewsets.ModelViewSet):
    queryset = PTScheme.objects.all()
    serializer_class = PTSchemeSerializer

class PTSchemeMethodViewSet(viewsets.ModelViewSet):
    queryset = PTSchemeMethod.objects.all()
    serializer_class = PTSchemeMethodSerializer

class ControlTestingViewSet(viewsets.ModelViewSet):
    queryset = ControlTesting.objects.all()
    serializer_class = ControlTestingSerializer

class ControlTestingMethodViewSet(viewsets.ModelViewSet):
    queryset = ControlTestingMethod.objects.all()
    serializer_class = ControlTestingMethodSerializer

class MeasurementUncertaintyViewSet(viewsets.ModelViewSet):
    queryset = MeasurementUncertainty.objects.all()
    serializer_class = MeasurementUncertaintySerializer
