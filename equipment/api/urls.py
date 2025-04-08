from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, CalibrationViewSet, InternalControlViewSet, RepairViewSet

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'calibration', CalibrationViewSet, basename='calibration')
router.register(r'internal-control', InternalControlViewSet, basename='internal-control')
router.register(r'repair', RepairViewSet, basename='repair')

urlpatterns = router.urls
