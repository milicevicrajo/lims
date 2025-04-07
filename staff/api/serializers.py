from rest_framework import serializers
from staff.models import (
    Staff,
    JobPosition,
    StaffJobPosition,
    ProfessionalExperience,
    TrainingCourse,
    MembershipInInternationalOrg,
    Training,
    TrainingTests,
    Authorization,
    AuthorizationType,
    NoMethodAuthorization,
    StaffMethodTraining
)

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = '__all__'

class StaffJobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffJobPosition
        fields = '__all__'

class ProfessionalExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalExperience
        fields = '__all__'

class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = '__all__'

class MembershipInInternationalOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipInInternationalOrg
        fields = '__all__'

class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'

class TrainingTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingTests
        fields = '__all__'

class AuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authorization
        fields = '__all__'

class AuthorizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizationType
        fields = '__all__'

class NoMethodAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoMethodAuthorization
        fields = '__all__'

class StaffMethodTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMethodTraining
        fields = '__all__'
