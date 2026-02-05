from django.urls import path
from airports.views import (AirportsListAPIView, AirportsRetrieveApiView,
                            CountryListModelAPIView, CountryRetrieveModelAPIView)


urlpatterns = [
    path('airport/', AirportsListAPIView.as_view(), name='airport-list'),
    path('airport/<int:pk>/', AirportsRetrieveApiView.as_view()),
    path('', CountryListModelAPIView.as_view(), name='country-list'),
    path('<int:pk>/', CountryRetrieveModelAPIView.as_view())]
