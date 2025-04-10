from rest_framework import viewsets
from rest_framework.decorators import action
from methods.models import Method, Standard, TestingArea, TestSubject, SubDiscipline
from .serializers import MethodSerializer, StandardSerializer, TestingAreaSerializer, TestSubjectSerializer, SubDisciplineSerializer
from methods.services import create_method, create_standard, update_standard, delete_standard
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from methods.models import Standard
from methods.api.serializers import StandardSerializer
from methods.services import create_standard, update_standard, delete_standard
from methods.services import create_testing_area, update_testing_area, delete_testing_area
from methods.services import create_test_subject, update_test_subject, delete_test_subject
from methods.services import create_subdiscipline, update_subdiscipline, delete_subdiscipline, get_subdiscipline_methods
from methods.services import (
    create_method,
    update_method,
    delete_method,
    update_method_equipment,
    get_method_detail_context,
)
@extend_schema(tags=['Standard'])
class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            standard = create_standard(request.data)
            serializer = self.get_serializer(standard)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_standard = update_standard(instance, request.data)
            serializer = self.get_serializer(updated_standard)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            delete_standard(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Testing Area'])
class TestingAreaViewSet(viewsets.ModelViewSet):
    queryset = TestingArea.objects.all()
    serializer_class = TestingAreaSerializer

    def create(self, request, *args, **kwargs):
        try:
            testing_area = create_testing_area(request.data)
            serializer = self.get_serializer(testing_area)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_area = update_testing_area(instance, request.data)
            serializer = self.get_serializer(updated_area)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            delete_testing_area(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Test Subject'])
class TestSubjectViewSet(viewsets.ModelViewSet):
    queryset = TestSubject.objects.all()
    serializer_class = TestSubjectSerializer

    def create(self, request, *args, **kwargs):
        try:
            test_subject = create_test_subject(request.data)
            serializer = self.get_serializer(test_subject)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_subject = update_test_subject(instance, request.data)
            serializer = self.get_serializer(updated_subject)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            delete_test_subject(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['SubDiscipline'])
class SubDisciplineViewSet(viewsets.ModelViewSet):
    queryset = SubDiscipline.objects.all()
    serializer_class = SubDisciplineSerializer

    def create(self, request, *args, **kwargs):
        try:
            subdiscipline = create_subdiscipline(request.data)
            serializer = self.get_serializer(subdiscipline)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_subdiscipline = update_subdiscipline(instance, request.data)
            serializer = self.get_serializer(updated_subdiscipline)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            delete_subdiscipline(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='methods')
    def methods(self, request, pk=None):
        """ Dodatni endpoint za metode unutar poddiscipline """
        subdiscipline = self.get_object()
        methods = get_subdiscipline_methods(subdiscipline)
        serializer = MethodSerializer(methods, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Method'])
class MethodViewSet(viewsets.ModelViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer

    def create(self, request, *args, **kwargs):
        try:
            method = create_method(request.data, request.user)
            serializer = self.get_serializer(method)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            updated_method = update_method(instance, request.data)
            serializer = self.get_serializer(updated_method)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            delete_method(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='equipment-options')
    def equipment_options(self, request, pk=None):
        """ Endpoint za selekciju opreme za metodu """
        method = self.get_object()
        equipment_queryset = get_user_equipment_queryset_for_method(request.user)
        serializer = EquipmentSerializer(equipment_queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='update-equipment')
    def update_equipment(self, request, pk=None):
        """ Endpoint za ažuriranje opreme u metodi """
        method = self.get_object()
        action = request.data.get('action')
        selected_equipment_id = request.data.get('equipment_id')

        if not selected_equipment_id or not action:
            return Response({'detail': 'Nedostaju podaci za ažuriranje.'}, status=status.HTTP_400_BAD_REQUEST)

        result = update_method_equipment(method, selected_equipment_id, action)

        if 'error' in result:
            return Response({'detail': result['error']}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='details')
    def method_details(self, request, pk=None):
        """ Endpoint za detalje metode """
        method = self.get_object()
        context = get_method_detail_context(method)
        return Response(context)