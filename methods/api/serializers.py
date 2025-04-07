from rest_framework import serializers
from methods.models import Method, Standard, TestingArea, TestSubject, SubDiscipline

class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = '__all__'

class TestingAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestingArea
        fields = '__all__'

class TestSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSubject
        fields = '__all__'

class SubDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDiscipline
        fields = '__all__'

class MethodSerializer(serializers.ModelSerializer):
    standard = StandardSerializer(read_only=True)
    testing_area = TestingAreaSerializer(read_only=True)
    test_subjects = TestSubjectSerializer(read_only=True)

    class Meta:
        model = Method
        fields = '__all__'
