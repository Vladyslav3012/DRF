from django.db import models
from django.core.exceptions import ValidationError

from users.models import CustomUser


class Flights(models.Model):
    status_choice = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled')
    ]

    flight_status = models.CharField(max_length=20,
                                     default="scheduled",
                                     choices=status_choice)
    city_departure = models.CharField(max_length=100)
    city_arrival = models.CharField(max_length=100)
    time_departure = models.DateTimeField()
    time_arrival = models.DateTimeField()
    tickets_count = models.PositiveSmallIntegerField()
    airplanes = models.ForeignKey('airplanes.Airplanes',
                                  on_delete=models.CASCADE,
                                  related_name="flights")

    def __str__(self):
        return (f"({self.get_flight_status_display()}) "
                f"{self.city_departure} --> {self.city_arrival}")

    def clean(self):
        if self.time_departure >= self.time_arrival:
            raise ValidationError("Departure time cannot"
                                  " be later than arrival time")
        if self.city_departure == self.city_arrival:
            raise ValidationError("Cities cannot match")
        if self.tickets_count > self.airplanes.count_of_seats:
            raise ValidationError(f"Count of tickets ({self.tickets_count}) "
                                  f"more than seats on board"
                                  f"({self.airplanes.count_of_seats})")


class Ticket(models.Model):
    ENUM = [
        ('econom', 'Econom class'),
        ('business', 'Business class'),
        ('first', 'First class'),
    ]
    ticket_class = models.CharField(max_length=20, choices=ENUM,
                                    default='econom')
    flight = models.ForeignKey(Flights,
                               on_delete=models.CASCADE,
                               related_name="tickets")
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.CASCADE,
                              related_name="tickets")
    time_of_purchase = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f' {self.flight}({self.get_ticket_class_display()})'
