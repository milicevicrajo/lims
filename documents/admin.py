from django.contrib import admin
from .models import *

admin.site.register(DocumentType)
admin.site.register(Document)
admin.site.register(DocumentVersion)
admin.site.register(DocumentAccessLog)

