from django.contrib import admin
from .models import Center, OrganizationalUnit, Laboratory, CustomUser

admin.site.register(Center)
admin.site.register(OrganizationalUnit)
admin.site.register(Laboratory)
admin.site.register(CustomUser)
# Compare this snippet from lims/equipment/models.py:
