from rest_framework.routers import DefaultRouter
from .views import MethodViewSet, StandardViewSet, TestingAreaViewSet, TestSubjectViewSet, SubDisciplineViewSet

router = DefaultRouter()
router.register(r'methods', MethodViewSet)
router.register(r'standards', StandardViewSet)
router.register(r'testing-areas', TestingAreaViewSet)
router.register(r'test-subjects', TestSubjectViewSet)
router.register(r'sub-disciplines', SubDisciplineViewSet)

urlpatterns = router.urls
