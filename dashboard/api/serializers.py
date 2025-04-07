from rest_framework import serializers
from equipment.models import Calibration

class CalibrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calibration
        fields = ['id', 'equipment', 'next_calibration_date', 'certificate_number']
