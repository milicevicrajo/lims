from rest_framework.routers import DefaultRouter
from equipment.api.views import EquipmentViewSet

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = router.urls
