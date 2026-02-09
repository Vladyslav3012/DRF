from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView,
                                   SpectacularRedocView)

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenRefreshView,
                                            TokenVerifyView)

import assistant.urls
import orders.urls
import users.urls
from airplanes.views import AirplanesViewSet, AirlinesViewSet
from flights.views import FlightsViewSet, TicketsViewSet
from airports import urls as AirportUrls
from orders.views import cancel, success
from .settings import DEBUG

router = DefaultRouter()

router.register(r'airlines', AirlinesViewSet, basename='airlines')
router.register(r'airplanes', AirplanesViewSet, basename='airplanes')
router.register(r'flights', FlightsViewSet, basename='flight')
router.register(r'tickets', TicketsViewSet, basename='ticket')


urlpatterns = [
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),

    path('admin/', admin.site.urls),

    path('api/v1/', include(router.urls)),
    path('api/v1/', include(users.urls)),
    path('api/v1/', include(orders.urls)),
    path('api/v1/country/', include(AirportUrls)),
    path('api/v1/gemini/', include(assistant.urls)),

    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

if DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
