from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
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
from staff.services import (
    get_active_staff_queryset,
    get_staff_object,
    create_staff,
    update_staff,
    delete_staff,
    get_staff_detail_context,
    create_professional_experience,
    update_professional_experience,
    delete_professional_experience,
    create_training_course,
    update_training_course,
    delete_training_course,
    create_membership,
    update_membership,
    delete_membership,
    create_training,
    update_training,
    delete_training,
    update_training_test,
    create_authorization_type,
    update_authorization_type,
    delete_authorization_type,
    create_authorization,
    update_authorization,
    delete_authorization
)

@extend_schema(tags=['Staff'])
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def get_queryset(self):
        return get_active_staff_queryset()

    @action(detail=True, methods=['get'], url_path='detail')
    def staff_detail(self, request, pk=None):
        """
        Detalji o osoblju — identično kao `StaffDetailView`
        """
        staff = get_staff_object(pk)
        context = get_staff_detail_context(staff)
        serializer = self.get_serializer(staff)
        return Response({
            'staff': serializer.data,
            'context': context
        })

    @action(detail=False, methods=['post'], url_path='create-custom')
    def create_custom(self, request):
        """
        Custom create sa servis logikom
        """
        try:
            staff = create_staff(request.data)
            serializer = self.get_serializer(staff)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-custom')
    def update_custom(self, request, pk=None):
        """
        Custom update sa servis logikom
        """
        try:
            staff = get_staff_object(pk)
            updated_staff = update_staff(staff, request.data)
            serializer = self.get_serializer(updated_staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete-custom')
    def delete_custom(self, request, pk=None):
        """
        Custom delete sa servis logikom
        """
        try:
            staff = get_staff_object(pk)
            delete_staff(staff)
            return Response({'detail': 'Uspešno obrisan zapis.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Job Position'])
class JobPositionViewSet(viewsets.ModelViewSet):
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_position = create_job_position(serializer.validated_data)
        output_serializer = self.get_serializer(job_position)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        job_position = update_job_position(instance, serializer.validated_data)
        output_serializer = self.get_serializer(job_position)

        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_job_position(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Staff Job Position'])
class StaffJobPositionViewSet(viewsets.ModelViewSet):
    queryset = StaffJobPosition.objects.all()
    serializer_class = StaffJobPositionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_job_position = create_staff_job_position(serializer.validated_data)
        output_serializer = self.get_serializer(staff_job_position)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        staff_job_position = update_staff_job_position(instance, serializer.validated_data)
        output_serializer = self.get_serializer(staff_job_position)

        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_staff_job_position(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@extend_schema(tags=['Professional Experience'])
class ProfessionalExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalExperience.objects.all()
    serializer_class = ProfessionalExperienceSerializer

    def perform_create(self, serializer):
        create_professional_experience(serializer.validated_data)

    def perform_update(self, serializer):
        update_professional_experience(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_professional_experience(instance)

@extend_schema(tags=['Training Course'])
class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer

    def perform_create(self, serializer):
        create_training_course(serializer.validated_data)

    def perform_update(self, serializer):
        update_training_course(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_training_course(instance)

@extend_schema(tags=['Membership In International Org'])
class MembershipInInternationalOrgViewSet(viewsets.ModelViewSet):
    queryset = MembershipInInternationalOrg.objects.all()
    serializer_class = MembershipInInternationalOrgSerializer

    def perform_create(self, serializer):
        create_membership(serializer.validated_data)

    def perform_update(self, serializer):
        update_membership(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_membership(instance)

@extend_schema(tags=['Training'])
class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

    def perform_create(self, serializer):
        # Koristi servis funkciju
        data = serializer.validated_data
        training = create_training(data, self.request.user)
        serializer.instance = training

    def perform_update(self, serializer):
        data = serializer.validated_data
        update_training(self.get_object(), data)

    def perform_destroy(self, instance):
        delete_training(instance)

@extend_schema(tags=['Training Tests'])
class TrainingTestsViewSet(viewsets.ModelViewSet):
    queryset = TrainingTests.objects.all()
    serializer_class = TrainingTestsSerializer

    def perform_update(self, serializer):
        update_training_test(self.get_object(), serializer.validated_data)

    # Ako dodaš kreiranje/brisanje za testove, dodaćemo i ovde!

@extend_schema(tags=['Authorization Type'])
class AuthorizationTypeViewSet(viewsets.ModelViewSet):
    queryset = AuthorizationType.objects.all()
    serializer_class = AuthorizationTypeSerializer

    def perform_create(self, serializer):
        create_authorization_type(serializer.validated_data)

    def perform_update(self, serializer):
        update_authorization_type(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_authorization_type(instance)


@extend_schema(tags=['Authorization'])
class AuthorizationViewSet(viewsets.ModelViewSet):
    queryset = Authorization.objects.all()
    serializer_class = AuthorizationSerializer

    def perform_create(self, serializer):
        create_authorization(serializer.validated_data)

    def perform_update(self, serializer):
        update_authorization(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_authorization(instance)
@extend_schema(tags=['Authorization'])
class NoMethodAuthorizationViewSet(viewsets.ModelViewSet):
    queryset = NoMethodAuthorization.objects.all()
    serializer_class = NoMethodAuthorizationSerializer

@extend_schema(tags=['Training'])
class StaffMethodTrainingViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    queryset = StaffMethodTraining.objects.all()
    serializer_class = StaffMethodTrainingSerializer
