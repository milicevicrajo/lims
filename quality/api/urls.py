from rest_framework.routers import DefaultRouter
from .views import (
    PTSchemeViewSet,
    PTSchemeMethodViewSet,
    ControlTestingViewSet,
    ControlTestingMethodViewSet,
    MeasurementUncertaintyViewSet
)

router = DefaultRouter()
router.register(r'pt-schemes', PTSchemeViewSet)
router.register(r'pt-scheme-methods', PTSchemeMethodViewSet)
router.register(r'control-testings', ControlTestingViewSet)
router.register(r'control-testing-methods', ControlTestingMethodViewSet)
router.register(r'measurement-uncertainties', MeasurementUncertaintyViewSet)

urlpatterns = router.urls
