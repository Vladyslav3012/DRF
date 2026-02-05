from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from custom_permission import IsAdminOrReadOnly, IsOwnerOrAdmin
from .models import Flights, Ticket
from .serializers import FlightsRetrieveSerializer, FlightListSerializer, TicketListSerializer, TicketRetrieveSerializer
from rest_framework import viewsets


@extend_schema(tags=['Flights'])
class FlightsViewSet(viewsets.ModelViewSet):
    queryset = Flights.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightsRetrieveSerializer


@extend_schema(tags=['Tickets'])
class TicketsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(owner=user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        return TicketRetrieveSerializer
