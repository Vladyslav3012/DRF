import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from airplanes.models import Airplanes
from .models import Ticket, Flights


logger = logging.getLogger(__name__)


class FlightsRetrieveSerializer(serializers.ModelSerializer):
    airplanes = serializers.SlugRelatedField(
        slug_field="model",
        queryset=Airplanes.objects.all()
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
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2,
                                             read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flights
        fields = ['id', 'flight_status',
                  'city_departure', 'city_arrival',
                  'time_departure', 'time_arrival',
                  'ticket_economy_price', 'ticket_business_price',
                  'ticket_first_price',
                  'tickets_count_economy', 'tickets_count_business',
                  'tickets_count_first', 'total_tickets',
                  'airplanes', 'average_price']

    def validate(self, attrs):
        def get_data(field_name, default=None):
            val = attrs.get(field_name)
            if val is None and self.instance:
                val = getattr(self.instance, field_name)
            return val if val is not None else default

        economy_tickets = get_data('tickets_count_economy', 0)
        business_tickets = get_data('tickets_count_business', 0)
        first_tickets = get_data('tickets_count_first', 0)

        total_tickets = sum([economy_tickets, business_tickets, first_tickets])

        time_departure = get_data('time_departure')
        time_arrival = get_data('time_arrival')

        city_departure = get_data('city_departure')
        city_arrival = get_data('city_arrival')

        airplanes = get_data('airplanes', None)

        if time_departure and time_arrival:
            if time_departure > time_arrival:
                logger.error("Departure time > arrival time")
                raise serializers.ValidationError("Departure time cannot be "
                                                  "later than arrival time.")

        if city_arrival and city_departure:
            if city_departure.lower() == city_arrival.lower():
                logger.error("city departure == city arrival")
                raise serializers.ValidationError("The arrival location must be different"
                                                  "from the departure location")

        if airplanes:
            if total_tickets > airplanes.total_seats:
                logger.error(f"{total_tickets} cannot be more than "
                             f"airplanes total seats{airplanes.total_seats}")
                raise serializers.ValidationError("The number of tickets cannot be more"
                                                  "than the number of seats on board")

            if economy_tickets > airplanes.economy_class_seats:
                logger.error(f"Count economy tickets {economy_tickets}"
                             f" more than airplanes economy seats"
                             f" {airplanes.economy_class_seats}")
                raise serializers.ValidationError("Number of economy tickets "
                                                  "exceeds airplane economy seats")

            if business_tickets > airplanes.business_class_seats:
                logger.error(f"Count business tickets {business_tickets}"
                             f" more than airplanes business seats"
                             f" {airplanes.business_class_seats}")
                raise serializers.ValidationError("Number of business tickets "
                                                  "exceeds airplane business seats")

            if first_tickets > airplanes.first_class_seats:
                logger.error(f"Count first tickets {first_tickets}"
                             f" more than airplanes first seats"
                             f" {airplanes.first_class_seats}")
                raise serializers.ValidationError("Number of first class tickets "
                                                  "exceeds airplane first class seats")

        if total_tickets == 0:
            logger.error("Total tickets == 0")
            raise serializers.ValidationError("Flight must have at least one ticket")

        return attrs


class FlightListSerializer(FlightsRetrieveSerializer):

    class Meta:
        model = Flights
        fields = ['id', 'flight_status',
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
                    logger.error(f"There is no such place on economy #{seat_number}")
                    raise serializers.ValidationError("Seat number exceeds economy class "
                                                      "seats on airplane")

            if ticket_class == "business":
                if seat_number > flight.airplanes.business_class_seats:
                    logger.error(f"There is no such place on business #{seat_number}")
                    raise serializers.ValidationError("Seat number exceeds business "
                                                      "class seats on airplane")

            if ticket_class == "first":
                if seat_number > flight.airplanes.first_class_seats:
                    logger.error(f"There is no such place on first #{seat_number}")
                    raise serializers.ValidationError("Seat number exceeds "
                                                      "first class seats on airplane")


class TicketListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='order.status', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_class', 'seat_number', 'status', 'flight']


class TicketRetrieveSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='order.status', read_only=True)
    currency = serializers.CharField(source='order.currency', read_only=True)

    class Meta:
        model = Ticket
        fields = ['ticket_class', 'seat_number', 'status',
                  'flight', 'price', 'currency']
