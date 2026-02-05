import factory
from orders.models import Order, Payment

class OrderFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Order
        skip_postgeneration_save = True

    owner = factory.SubFactory('users.tests.factories.UserFactory')
    currency = Order.CurrencyChoice.USD
    quantity = 1
