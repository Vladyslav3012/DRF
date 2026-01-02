from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from custom_permission import  IsOwnerOrAdmin
from .models import Ticket, Flights
from .serializers import TicketSerializer, FlightsSerializer
from rest_framework import viewsets



class FlightsAPI(viewsets.ModelViewSet):
    serializer_class = FlightsSerializer
    queryset = Flights.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['time_departure', ]





class TicketAPI(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin )
    #
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return Ticket.objects.all()
    #     return Ticket.objects.filter(owner=user)



