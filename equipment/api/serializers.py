from rest_framework import serializers
from equipment.models import Equipment, Calibration, InternalControl, Repair

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class CalibrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calibration
        fields = '__all__'

class InternalControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalControl
        fields = '__all__'

class RepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repair
        fields = '__all__'


