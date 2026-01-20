from django.contrib import admin
from .models import CustomUser, Order, Payment

admin.site.register([CustomUser, Order, Payment])
