from rest_framework import serializers
from core.models import Center, OrganizationalUnit, Laboratory, CustomUser

class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Center
        fields = '__all__'

class OrganizationalUnitSerializer(serializers.ModelSerializer):
    center = CenterSerializer(read_only=True)

    class Meta:
        model = OrganizationalUnit
        fields = '__all__'

class LaboratorySerializer(serializers.ModelSerializer):
    organizational_unit = OrganizationalUnitSerializer(read_only=True)

    class Meta:
        model = Laboratory
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    laboratory = LaboratorySerializer(read_only=True)
    laboratory_permissions = LaboratorySerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'laboratory', 'laboratory_permissions']
