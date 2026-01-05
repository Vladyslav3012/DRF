from rest_framework import serializers
from rest_framework.settings import api_settings
from airplanes.models import Airplanes

from .models import Ticket, Flights

class FlightsSerializer(serializers.ModelSerializer):
    airplanes = serializers.SlugRelatedField(
        slug_field="model",
        queryset=Airplanes.objects.all()
    )
    flight_status_name = serializers.CharField(source="get_flight_status_display", read_only=True)
    class Meta:
        model = Flights
        fields = ['id', 'flight_status','flight_status_name', 'flight_status',
                  'city_departure', 'city_arrival',
                  'time_departure', 'time_arrival', 'tickets_count',
                  'airplanes']
    def validate(self, attrs):
        if attrs.get('time_departure') > attrs.get('time_arrival'):
            raise serializers.ValidationError("Час прибуття не може бути пізнішим"
                                              "за виліт")
        if attrs.get('city_departure').lower() == attrs.get('city_arrival').lower():
            raise serializers.ValidationError("Місце прибуття повинно відрізнятись"
                                              "від місця вильоту")
        if attrs.get('tickets_count') > attrs.get('airplanes').count_of_seats:
            raise serializers.ValidationError("Кількість квитків не може бути більшою"
                                              "за кількість місць на борту")
        return attrs

class TicketSerializer(serializers.ModelSerializer):
    ticket_class_name = serializers.CharField(source="get_ticket_class_display", read_only=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Ticket
        fields = ['ticket_class', 'ticket_class_name', 'flight', 'owner']

