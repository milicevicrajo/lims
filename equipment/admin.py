from django.contrib import admin
from .models import Equipment, Calibration, InternalControl, Repair

admin.site.register(Equipment)
admin.site.register(Calibration)
admin.site.register(InternalControl)
admin.site.register(Repair)
