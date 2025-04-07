from django.urls import path
from .views import UpcomingCalibrationsAPIView

urlpatterns = [
    path('upcoming-calibrations/', UpcomingCalibrationsAPIView.as_view(), name='upcoming-calibrations'),
]
