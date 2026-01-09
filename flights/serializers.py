from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from airplanes.models import Airplanes
from .models import Ticket, Flights


class FlightsRetrieveSerializer(serializers.ModelSerializer):
    airplanes = serializers.SlugRelatedField(
        slug_field="model",
        queryset=Airplanes.objects.all()
    )
    flight_status_name = serializers.CharField(
        source="get_flight_status_display",
        read_only=True
    )
    ticket_economy_price = serializers.DecimalField(min_value=0, max_value=1000,
                                                    default=0, max_digits=10,
                                                    decimal_places=2)
    ticket_business_price = serializers.DecimalField(min_value=0, max_value=1000,
                                                     default=0, max_digits=10,
                                                     decimal_places=2)
    ticket_first_price = serializers.DecimalField(min_value=0, max_value=1000,
                                                  default=0, max_digits=10,
                                                  decimal_places=2,)
    tickets_count_economy = serializers.IntegerField(min_value=0, max_value=100)
    tickets_count_business = serializers.IntegerField(min_value=0, max_value=100)
    tickets_count_first = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Flights
        fields = ['id', 'flight_status_name', 'flight_status',
                  'city_departure', 'city_arrival',
                  'time_departure', 'time_arrival',
                  'ticket_economy_price', 'ticket_business_price',
                  'ticket_first_price',
                  'tickets_count_economy', 'tickets_count_business',
                  'tickets_count_first', 'total_tickets',
                  'airplanes']

    def validate(self, attrs):

        economy_tickets = attrs.get('tickets_count_economy', 0)
        business_tickets = attrs.get('tickets_count_business', 0)
        first_tickets = attrs.get('tickets_count_first', 0)
        total_tickets = sum([economy_tickets, business_tickets, first_tickets])
        airplanes = attrs.get('airplanes')

        if attrs.get('time_departure') > attrs.get('time_arrival'):
            raise serializers.ValidationError("Departure time cannot be "
                                              "later than arrival time.")
        if attrs.get('city_departure').lower() == attrs.get('city_arrival').lower():
            raise serializers.ValidationError("The arrival location must be different"
                                              "from the departure location")
        if total_tickets > airplanes.total_seats:
            raise serializers.ValidationError("The number of tickets cannot be more"
                                              "than the number of seats on board")
        if business_tickets > airplanes.business_class_seats:
            raise serializers.ValidationError("Number of business tickets "
                                              "exceeds airplane business seats")
        if first_tickets > airplanes.first_class_seats:
            raise serializers.ValidationError("Number of first class tickets "
                                              "exceeds airplane first class seats")
        if economy_tickets > airplanes.economy_class_seats:
            raise serializers.ValidationError("Number of economy tickets "
                                              "exceeds airplane economy seats")
        if total_tickets == 0:
            raise serializers.ValidationError("Flight must have at least one ticket")

        return attrs


class FlightListSerializer(FlightsRetrieveSerializer):

    class Meta:
        model = Flights
        fields = ['id', 'flight_status_name',
                  'city_departure', 'city_arrival',
                  'total_tickets', 'average_price']


class TicketCreateSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(min_value=1, max_value=300)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    flight = serializers.PrimaryKeyRelatedField(queryset=Flights.objects.all())

    class Meta:
        model = Ticket
        fields = ['ticket_class', 'seat_number',
                  'flight', 'owner',]
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=['flight', 'seat_number', 'ticket_class']
            )
        ]

        def validate(self, attrs):
            ticket_class = attrs.get('ticket_class')
            seat_number = attrs.get('seat_number')
            flight = attrs.get('flight')\

            if ticket_class == "economy":
                if seat_number > flight.airplanes.economy_class_seats:
                    raise serializers.ValidationError("Seat number exceeds economy class "
                                                      "seats on airplane")

            if ticket_class == "business":
                if seat_number > flight.airplanes.business_class_seats:
                    raise serializers.ValidationError("Seat number exceeds business "
                                                      "class seats on airplane")

            if ticket_class == "first":
                if seat_number > flight.airplanes.first_class_seats:
                    raise serializers.ValidationError("Seat number exceeds "
                                                      "first class seats on airplane")
