from drf_spectacular.utils import extend_schema
from custom_permission import IsAdminOrReadOnly
from .models import Flights
from .serializers import FlightsRetrieveSerializer, FlightListSerializer
from rest_framework import viewsets


@extend_schema(tags=['Flights'])
class FlightsViewSet(viewsets.ModelViewSet):
    queryset = Flights.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightsRetrieveSerializer
