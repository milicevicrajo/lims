from django.contrib import admin
from .models import *
# Compare this snippet from lims/quality/models.py:

admin.site.register(PTScheme)
admin.site.register(PTSchemeMethod)
admin.site.register(ControlTesting)
admin.site.register(ControlTestingMethod)
admin.site.register(MeasurementUncertainty)


