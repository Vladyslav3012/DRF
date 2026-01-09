from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from users.models import CustomUser


class Flights(models.Model):
    class StatusChoice(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        BOARDING = "boarding", "Boarding"
        DEPARTED = "departed", "Departed"
        DELAYED = "delayed", "Delayed"
        CANCELLED = "cancelled", "Cancelled"

    flight_status = models.CharField(max_length=20,
                                     default=StatusChoice.SCHEDULED,
                                     choices=StatusChoice.choices)
    city_departure = models.CharField(max_length=100)
    city_arrival = models.CharField(max_length=100)
    time_departure = models.DateTimeField()
    time_arrival = models.DateTimeField()
    tickets_count_economy = models.PositiveSmallIntegerField(default=0)
    tickets_count_business = models.PositiveSmallIntegerField(default=0)
    tickets_count_first = models.PositiveSmallIntegerField(default=0)
    ticket_economy_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_business_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_first_price = models.DecimalField(max_digits=10, decimal_places=2)
    airplanes = models.ForeignKey('airplanes.Airplanes',
                                  on_delete=models.CASCADE,
                                  related_name="flights")

    @property
    def average_price(self):
        return str((self.ticket_economy_price
                    + self.ticket_business_price
                    + self.ticket_first_price) / 3) + "$"

    @property
    def total_tickets(self):
        return sum([self.tickets_count_business,
                    self.tickets_count_first,
                    self.tickets_count_economy])

    def clean(self):
        airplane = self.airplanes

        if self.time_departure >= self.time_arrival:
            raise ValidationError("Departure time cannot"
                                  " be later than arrival time")
        if self.city_departure == self.city_arrival:
            raise ValidationError("Cities cannot match")
        if self.tickets_count_business > airplane.business_class_seats:
            raise ValidationError("Number of business tickets "
                                  "exceeds airplane business seats")
        if self.tickets_count_first > airplane.first_class_seats:
            raise ValidationError("Number of first class tickets "
                                  "exceeds airplane first class seats")
        if self.tickets_count_economy > airplane.economy_class_seats:
            raise ValidationError("Number of economy tickets "
                                  "exceeds airplane economy seats")
        if self.total_tickets == 0:
            raise ValidationError("Flight must have at least one ticket")

    def __str__(self):
        return (f"({self.get_flight_status_display()}) "
                f"{self.city_departure} --> {self.city_arrival}")


class Ticket(models.Model):

    class ClassChoice(models.TextChoices):
        ECONOMY = "economy"
        BUSINESS = "business"
        FIRST = "first"

    ticket_class = models.CharField(max_length=20,
                                    choices=ClassChoice.choices,
                                    default=ClassChoice.ECONOMY)
    seat_number = models.PositiveIntegerField()

    order = models.ForeignKey('users.Order', on_delete=models.CASCADE,
                              null=True, blank=True, related_name="tickets"
                              )
    flight = models.ForeignKey(Flights,
                               on_delete=models.CASCADE,
                               related_name="tickets")
    owner = models.ForeignKey(CustomUser,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL,
                              related_name="tickets")

    @property
    def price(self):
        rates = {
            'usd': Decimal(1),
            'eur': Decimal(0.84),
            'uah': Decimal(42.8)
        }

        class_price = {
            'economy': self.flight.ticket_economy_price,
            'business': self.flight.ticket_business_price,
            'first': self.flight.ticket_first_price,
        }

        currency_pr = self.order.currency
        ticket_class = self.ticket_class

        if ticket_class not in class_price:
            raise ValidationError("Select correct ticket class")

        return class_price[ticket_class] * rates[currency_pr]

    def clean(self):
        if self.seat_number > self.flight.airplanes.total_seats:
            raise ValidationError("Seat number exceeds total seats on airplane")

    def __str__(self):
        return f' {self.flight}({self.get_ticket_class_display()}, Seat: {self.seat_number})'
