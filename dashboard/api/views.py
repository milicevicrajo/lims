from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboard.views import get_upcoming_calibrations  # iskoristi postojeću funkciju
from .serializers import CalibrationSerializer  # napravi serializer

class UpcomingCalibrationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        upcoming_calibrations = get_upcoming_calibrations(request.user)

        # Serializuj podatke
        serializer = CalibrationSerializer(upcoming_calibrations, many=True)

        return Response(serializer.data)
