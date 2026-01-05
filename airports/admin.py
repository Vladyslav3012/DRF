from django.contrib import admin
from .models import Country, Airports

admin.site.register([Country, Airports])
