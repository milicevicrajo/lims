from rest_framework.routers import DefaultRouter
from .views import CenterViewSet, OrganizationalUnitViewSet, LaboratoryViewSet, UserViewSet
from django.urls import path, include

router = DefaultRouter()
router = DefaultRouter()

urlpatterns = router.urls
router.register(r'centers', CenterViewSet, basename='centers')
router.register(r'org-units', OrganizationalUnitViewSet)
router.register(r'laboratories', LaboratoryViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
