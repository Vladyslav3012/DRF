from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView,
                                   SpectacularRedocView)
from rest_framework.routers import DefaultRouter
from airports.views import (AirportsListAPIView, AirportsRetrieveApiView,
                            CountryListModelAPIView, CountryRetrieveModelAPIView)
from airplanes.views import AirplanesViewSet, AirlinesViewSet
from flights.views import FlightsViewSet, TicketViewSet

router = DefaultRouter()

router.register(r'airlines', AirlinesViewSet)
router.register(r'airplanes', AirplanesViewSet)
router.register(r'flights', FlightsViewSet)
router.register(r'tickets', TicketViewSet, basename="tickets")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls')),

    path('api/v1/airports/', AirportsListAPIView.as_view()),
    path('api/v1/airports/<int:pk>/', AirportsRetrieveApiView.as_view()),

    path('api/v1/country/', CountryListModelAPIView.as_view()),
    path('api/v1/country/<int:pk>', CountryRetrieveModelAPIView.as_view()),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
