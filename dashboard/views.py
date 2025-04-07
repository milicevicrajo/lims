from datetime import datetime, timedelta
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery, F

from equipment.models import Calibration, Equipment

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services import get_upcoming_calibrations


@login_required
def index(request):
    upcoming_expirations = get_upcoming_calibrations(request.user)

    context = {
        'upcoming_calibrations': upcoming_expirations,
    }
    return render(request, 'dashboard/index.html', context)
