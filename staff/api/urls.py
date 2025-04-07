from rest_framework.routers import DefaultRouter
from .views import (
    StaffViewSet,
    JobPositionViewSet,
    StaffJobPositionViewSet,
    ProfessionalExperienceViewSet,
    TrainingCourseViewSet,
    MembershipInInternationalOrgViewSet,
    TrainingViewSet,
    TrainingTestsViewSet,
    AuthorizationViewSet,
    AuthorizationTypeViewSet,
    NoMethodAuthorizationViewSet,
    StaffMethodTrainingViewSet
)

router = DefaultRouter()
router.register(r'staff', StaffViewSet)
router.register(r'job-positions', JobPositionViewSet)
router.register(r'staff-job-positions', StaffJobPositionViewSet)
router.register(r'professional-experiences', ProfessionalExperienceViewSet)
router.register(r'training-courses', TrainingCourseViewSet)
router.register(r'memberships', MembershipInInternationalOrgViewSet)
router.register(r'trainings', TrainingViewSet)
router.register(r'training-tests', TrainingTestsViewSet)
router.register(r'authorizations', AuthorizationViewSet)
router.register(r'authorization-types', AuthorizationTypeViewSet)
router.register(r'no-method-authorizations', NoMethodAuthorizationViewSet)
router.register(r'staff-method-trainings', StaffMethodTrainingViewSet)

urlpatterns = router.urls
