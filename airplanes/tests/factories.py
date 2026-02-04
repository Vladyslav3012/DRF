import factory
from airplanes.models import Airplanes, Airlines
from airports.tests.factories import AirportsFactory


class AirlinesFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Airlines

    title = factory.Sequence(lambda n: f"Airline {n}")
    detail = factory.Sequence(lambda n: f"About airlines {n}")
    data_of_create = "2026-02-04"
    slogan = factory.Sequence(lambda n: f"Slogan airline {n}")
    airport = factory.SubFactory(AirportsFactory)


class AirplanesFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Airplanes

    model = factory.Sequence(lambda n: f"Airplane {n}")
    economy_class_seats = 10
    business_class_seats = 10
    first_class_seats = 10
    airlines = factory.SubFactory(AirlinesFactory)