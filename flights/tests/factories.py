import factory
from django.utils.dateparse import parse_datetime

from airplanes.tests.factories import AirplanesFactory
from flights.models import Flights, Ticket


class FlightsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Flights
        skip_postgeneration_save = True

    city_departure = factory.Sequence(lambda n: f"City departure {n}")
    city_arrival = factory.Sequence(lambda n: f"City arrival{n}")
    time_departure = parse_datetime("2026-02-05T10:07:20.910Z")
    time_arrival = parse_datetime("2026-03-05T10:07:20.910Z")
    tickets_count_economy = 10
    tickets_count_business = 10
    tickets_count_first = 10
    ticket_economy_price = "10.00"
    ticket_business_price = "15.00"
    ticket_first_price = "20.00"
    airplanes = factory.SubFactory(AirplanesFactory)