from django.db import models
from django.core.exceptions import ValidationError

from users.models import CustomUser


class Flights(models.Model):
    status_choice = [
        ('scheduled', 'Запланований'),
        ('boarding', 'Посадка'),
        ('departed', 'Вилетів'),
        ('delayed', 'Затриманий'),
        ('cancelled', 'Відмінений')
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
        return f"({self.get_flight_status_display()}) {self.city_departure} --> {self.city_arrival}"

    def clean(self):
        if self.time_departure >= self.time_arrival:
            raise ValidationError("Час прибуття має бути пізніше за виліт ")
        if self.city_departure == self.city_arrival:
            raise ValidationError("Міста не можуть співпадати")
        if self.tickets_count > self.airplanes.count_of_seats:
            raise ValidationError(f"Кількість квитків ({self.tickets_count}) "
                                  f"більше чим місць на борту ({self.airplanes.count_of_seats})")


class Ticket(models.Model):
    ENUM = [
        ('econom', 'Низький клас'),
        ('business', 'Бізнес клас'),
        ('first', 'Перший клас'),
    ]
    ticket_class = models.CharField(max_length=20,choices=ENUM, default='econom')
    flight = models.ForeignKey(Flights,
                               on_delete=models.CASCADE,
                               related_name="tickets")
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.CASCADE,
                              related_name="tickets"
    )

    def __str__(self):
        return f' {self.flight}({self.get_ticket_class_display()})'



