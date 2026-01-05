from django.contrib import admin
from .models import Flights, Ticket

admin.site.register([Flights, Ticket])
