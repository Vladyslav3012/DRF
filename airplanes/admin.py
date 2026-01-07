from django.contrib import admin
from .models import Airlines, Airplanes

admin.site.register([Airlines, Airplanes])
