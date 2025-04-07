from rest_framework import viewsets
from methods.models import Method, Standard, TestingArea, TestSubject, SubDiscipline
from .serializers import MethodSerializer, StandardSerializer, TestingAreaSerializer, TestSubjectSerializer, SubDisciplineSerializer

class MethodViewSet(viewsets.ModelViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer

class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer

class TestingAreaViewSet(viewsets.ModelViewSet):
    queryset = TestingArea.objects.all()
    serializer_class = TestingAreaSerializer

class TestSubjectViewSet(viewsets.ModelViewSet):
    queryset = TestSubject.objects.all()
    serializer_class = TestSubjectSerializer

class SubDisciplineViewSet(viewsets.ModelViewSet):
    queryset = SubDiscipline.objects.all()
    serializer_class = SubDisciplineSerializer
