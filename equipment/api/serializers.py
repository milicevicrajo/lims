from rest_framework import serializers
from equipment.models import Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'  # ili izlistaj ručno ako hoćeš kontrolu
