from rest_framework import viewsets
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
from .serializers import (
    StaffSerializer,
    JobPositionSerializer,
    StaffJobPositionSerializer,
    ProfessionalExperienceSerializer,
    TrainingCourseSerializer,
    MembershipInInternationalOrgSerializer,
    TrainingSerializer,
    TrainingTestsSerializer,
    AuthorizationSerializer,
    AuthorizationTypeSerializer,
    NoMethodAuthorizationSerializer,
    StaffMethodTrainingSerializer
)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class JobPositionViewSet(viewsets.ModelViewSet):
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

class StaffJobPositionViewSet(viewsets.ModelViewSet):
    queryset = StaffJobPosition.objects.all()
    serializer_class = StaffJobPositionSerializer

class ProfessionalExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalExperience.objects.all()
    serializer_class = ProfessionalExperienceSerializer

class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer

class MembershipInInternationalOrgViewSet(viewsets.ModelViewSet):
    queryset = MembershipInInternationalOrg.objects.all()
    serializer_class = MembershipInInternationalOrgSerializer

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

class TrainingTestsViewSet(viewsets.ModelViewSet):
    queryset = TrainingTests.objects.all()
    serializer_class = TrainingTestsSerializer

class AuthorizationViewSet(viewsets.ModelViewSet):
    queryset = Authorization.objects.all()
    serializer_class = AuthorizationSerializer

class AuthorizationTypeViewSet(viewsets.ModelViewSet):
    queryset = AuthorizationType.objects.all()
    serializer_class = AuthorizationTypeSerializer

class NoMethodAuthorizationViewSet(viewsets.ModelViewSet):
    queryset = NoMethodAuthorization.objects.all()
    serializer_class = NoMethodAuthorizationSerializer

class StaffMethodTrainingViewSet(viewsets.ModelViewSet):
    queryset = StaffMethodTraining.objects.all()
    serializer_class = StaffMethodTrainingSerializer
