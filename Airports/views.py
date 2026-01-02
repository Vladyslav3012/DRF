from .models import Airports, Country
from .serializers import AirportSerializer, CountrySerializer
from rest_framework import viewsets
from custom_permission import IsAdminOrReadOnly


class CountryAPI(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()



class AirportsAPI(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airports.objects.all()


