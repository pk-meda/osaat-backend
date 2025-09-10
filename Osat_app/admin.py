from django.contrib import admin
from .models import Dispensing,school  # Import your model

admin.site.register(Dispensing)  # Register it
admin.site.register(school)
