import uuid

from django.db import models

from users.models import CustomUser


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING = "Pending", "Pending"
        CONFIRMED = "Confirmed", "Confirmed"
        EXPIRED = "Expired", "Expired"

    class CurrencyChoice(models.TextChoices):
        USD = "usd", "USD"
        UAH = "uah", "UAH"
        EURO = "eur", "EUR"

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    stripe_checkout_session = models.CharField(max_length=255,
                                               blank=True,
                                               null=True)
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.CASCADE,
                              related_name="orders")
    currency = models.CharField(max_length=10,
                                choices=CurrencyChoice.choices,
                                default=CurrencyChoice.USD)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,
                              choices=StatusChoice.choices,
                              default=StatusChoice.PENDING)
    quantity = models.PositiveIntegerField()

    @property
    def total_price(self):
        return sum(ticket.price for ticket in self.tickets.all())

    def __str__(self):
        return f"Order {self.order_id} by {self.owner.username}"


class Payment(models.Model):

    class CurrencyChoice(models.TextChoices):
        USD = "usd", "USD"
        UAH = "uah", "UAH"
        EURO = "eur", "EUR"

    class StatusChoice(models.TextChoices):
        PENDING = "Pending", "Pending"
        CONFIRMED = "Confirmed", "Confirmed"
        CANCELED = "Canceled", "Canceled"

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="payments")
    stripe_checkout_session = models.CharField(max_length=255, db_index=True)
    checkout_url = models.URLField(blank=True, null=True, max_length=2048)
    session_expires_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.CASCADE,
                              related_name="payments")
    status_payment = models.CharField(max_length=25,
                                      choices=StatusChoice.choices,
                                      default=StatusChoice.PENDING)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    currency = models.CharField(max_length=20,
                                choices=CurrencyChoice.choices,
                                default=CurrencyChoice.USD)
    created_at = models.DateTimeField(auto_now_add=True)
    payed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"({self.status_payment}) Payment {self.payment_id}, by {self.owner}"

