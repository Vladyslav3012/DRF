from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from Airports.views import AirportsAPI, CountryAPI
from airplanes.views import AirplanesAPI, AirlinesAPI
from Flights.views import FlightsAPI, TicketAPI

router = DefaultRouter()

router.register(r'country', CountryAPI)
router.register(r'airports', AirportsAPI)
router.register(r'airlines', AirlinesAPI)
router.register(r'airplanes', AirplanesAPI)
router.register(r'flights', FlightsAPI)
router.register(r'tickets', TicketAPI, basename="tickets")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
