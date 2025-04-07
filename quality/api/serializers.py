from rest_framework import serializers
from quality.models import (
    PTScheme,
    PTSchemeMethod,
    ControlTesting,
    ControlTestingMethod,
    MeasurementUncertainty
)

class PTSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTScheme
        fields = '__all__'

class PTSchemeMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTSchemeMethod
        fields = '__all__'

class ControlTestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlTesting
        fields = '__all__'

class ControlTestingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlTestingMethod
        fields = '__all__'

class MeasurementUncertaintySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUncertainty
        fields = '__all__'
