import factory
from airports.models import Airports, Country


class CountryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Country
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Country{n}")
    capital = factory.Sequence(lambda n: f"C{n:03d}")


class AirportsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Airports
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Airport{n}")
    address = factory.Sequence(lambda n: f"Address{n}")
    contact = factory.Sequence(lambda n: f"Number {n}")
    country = factory.SubFactory(CountryFactory)
