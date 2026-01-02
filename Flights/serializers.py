from rest_framework import serializers
from .models import Ticket, Flights

class FlightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flights
        fields = "__all__"

class TicketSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ['id']