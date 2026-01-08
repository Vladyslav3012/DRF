from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from custom_permission import IsOwnerOrAdmin, IsAdminOrReadOnly
from .models import Ticket, Flights
from .serializers import (TicketCreateSerializer, TicketListSerializer,
                          TicketRetrieveSerializer, FlightsSerializer)
from rest_framework import viewsets


class FlightsViewSet(viewsets.ModelViewSet):
    serializer_class = FlightsSerializer
    queryset = Flights.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['time_departure', ]


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            context["is_admin"] = True
        else:
            context["is_admin"] = False
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "create":
            return TicketCreateSerializer
        return TicketRetrieveSerializer
