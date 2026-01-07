from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView,
                                   SpectacularRedocView)

from rest_framework.routers import DefaultRouter
from airplanes.views import AirplanesViewSet, AirlinesViewSet
from flights.views import FlightsViewSet, TicketViewSet
# from users.views import UserViewSet
from airports import urls as AirportURLS

router = DefaultRouter()

router.register(r'airlines', AirlinesViewSet)
router.register(r'airplanes', AirplanesViewSet)
router.register(r'flights', FlightsViewSet)
router.register(r'tickets', TicketViewSet, basename="tickets")
# router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include(router.urls)),
    path('api/v1/country', include(AirportURLS)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
