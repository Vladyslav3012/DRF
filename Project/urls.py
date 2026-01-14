from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView,
                                   SpectacularRedocView)

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenRefreshView,
                                            TokenVerifyView)
import users.urls
from airplanes.views import AirplanesViewSet, AirlinesViewSet
from flights.views import FlightsViewSet
from airports import urls as AirportUrls
from users.views import cancel, success

router = DefaultRouter()

router.register(r'airlines', AirlinesViewSet)
router.register(r'airplanes', AirplanesViewSet)
router.register(r'flights', FlightsViewSet)


urlpatterns = [
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),

    path('admin/', admin.site.urls),

    path('api/v1/', include(router.urls)),
    path('api/v1/country/', include(AirportUrls)),

    path('api/v1/', include(users.urls)),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
