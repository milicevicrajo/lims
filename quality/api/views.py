from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
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
from quality.services import create_measurement_uncertainty, process_pt_scheme_form, get_pt_scheme_fields
from django.shortcuts import get_object_or_404
from quality.services import create_control_testing, update_control_testing

@extend_schema(tags=['PT Scheme'])
class PTSchemeViewSet(viewsets.ModelViewSet):
    queryset = PTScheme.objects.all()
    serializer_class = PTSchemeSerializer

    @action(detail=False, methods=['post'], url_path='create-with-methods')
    def create_with_methods(self, request):
        """
        Kreiranje PT Scheme zajedno sa metodama.
        Frontend šalje: 
        {
            "scheme_data": {...},
            "methods_data": [{...}, {...}]
        }
        """
        scheme_data = request.data.get('scheme_data')
        methods_data = request.data.get('methods_data')
        number_of_methods = len(methods_data)

        if not scheme_data or not methods_data:
            return Response({'detail': 'Podaci o šemi i metodama su obavezni.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pt_scheme, scheme_form, method_formset = process_pt_scheme_form(
                scheme_data,
                None,
                number_of_methods,
                methods_data=methods_data,
                user=request.user
            )

            if pt_scheme:
                serializer = self.get_serializer(pt_scheme)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Neuspešno kreiranje PT šeme.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='fields')
    def scheme_fields(self, request, pk=None):
        """ Vraća polja PT Scheme za frontend prikaz """
        scheme = self.get_object()
        fields = get_pt_scheme_fields(scheme)
        return Response(fields)


@extend_schema(tags=['PT Scheme Method'])
class PTSchemeMethodViewSet(viewsets.ModelViewSet):
    queryset = PTSchemeMethod.objects.all()
    serializer_class = PTSchemeMethodSerializer

    @action(detail=True, methods=['post'], url_path='assign-staff')
    def assign_staff(self, request, pk=None):
        """
        Povezivanje osoblja na metodu PT šeme
        Frontend šalje:
        {
            "staff_ids": [1, 2, 3]
        }
        """
        pt_scheme_method = self.get_object()
        staff_ids = request.data.get('staff_ids', [])

        if not staff_ids:
            return Response({'detail': 'Morate proslediti listu staff ID-jeva.'}, status=status.HTTP_400_BAD_REQUEST)

        pt_scheme_method.staff.set(staff_ids)
        pt_scheme_method.save()

        return Response({'detail': 'Osoblje uspešno dodeljeno.'}, status=status.HTTP_200_OK)

@extend_schema(tags=['Control Testing'])
class ControlTestingViewSet(viewsets.ModelViewSet):
    queryset = ControlTesting.objects.all()
    serializer_class = ControlTestingSerializer

    @action(detail=False, methods=['post'], url_path='create-with-methods')
    def create_with_methods(self, request):
        """
        Kreiranje Control Testing zajedno sa metodama.
        Frontend šalje:
        {
            "control_data": {...},
            "methods_data": [{...}, {...}]
        }
        """
        control_data = request.data.get('control_data')
        methods_data = request.data.get('methods_data')
        number_of_methods = len(methods_data)

        if not control_data or not methods_data:
            return Response({'detail': 'Podaci o kontrolnom ispitivanju i metodama su obavezni.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            control_testing, control_form, method_formset = create_control_testing(
                control_data,
                None,
                number_of_methods,
                methods_data=methods_data
            )

            if control_testing:
                serializer = self.get_serializer(control_testing)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Neuspešno kreiranje kontrolnog ispitivanja.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-control')
    def update_control(self, request, pk=None):
        """
        Update postojećeg Control Testing zapisa.
        """
        control_testing = self.get_object()

        try:
            success, errors = update_control_testing(control_testing, request.data, None)

            if success:
                serializer = self.get_serializer(control_testing)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Control Testing Method'])
class ControlTestingMethodViewSet(viewsets.ModelViewSet):
    queryset = ControlTestingMethod.objects.all()
    serializer_class = ControlTestingMethodSerializer

    @action(detail=True, methods=['post'], url_path='assign-staff')
    def assign_staff(self, request, pk=None):
        """
        Dodeli osoblje metodi kontrolnog ispitivanja.
        Frontend šalje:
        {
            "staff_ids": [1, 2, 3]
        }
        """
        control_testing_method = self.get_object()
        staff_ids = request.data.get('staff_ids', [])

        if not staff_ids:
            return Response({'detail': 'Morate proslediti listu staff ID-jeva.'}, status=status.HTTP_400_BAD_REQUEST)

        control_testing_method.staff.set(staff_ids)
        control_testing_method.save()

        return Response({'detail': 'Osoblje uspešno dodeljeno.'}, status=status.HTTP_200_OK)

@extend_schema(tags=['Measurement Uncertainty'])
class MeasurementUncertaintyViewSet(viewsets.ModelViewSet):
    queryset = MeasurementUncertainty.objects.all()
    serializer_class = MeasurementUncertaintySerializer

    @action(detail=False, methods=['post'], url_path='create-custom')
    def create_custom(self, request):
        """
        Custom kreiranje Measurement Uncertainty preko servisa.
        """
        try:
            instance = create_measurement_uncertainty(request.data, request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-custom')
    def update_custom(self, request, pk=None):
        """
        Custom update Measurement Uncertainty preko servisa.
        """
        instance = self.get_object()
        try:
            update_measurement_uncertainty(instance, request.data)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete-custom')
    def delete_custom(self, request, pk=None):
        """
        Custom brisanje Measurement Uncertainty preko servisa.
        """
        instance = self.get_object()
        try:
            delete_measurement_uncertainty(instance)
            return Response({'detail': 'Measurement uncertainty je uspešno obrisan.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
