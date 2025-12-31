from django.db import models
from django.core.exceptions import ValidationError

class Flights(models.Model):
    city_departure = models.CharField(max_length=100)
    city_arrival = models.CharField(max_length=100)
    time_departure = models.DateTimeField()
    time_arrival = models.DateTimeField()
    tickets_count = models.PositiveIntegerField()
    airplanes = models.ForeignKey('airplanes.Airplanes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.city_departure} --> {self.city_arrival}"

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
        ('first', 'Перший клас')
    ]
    flight = models.ForeignKey(Flights, on_delete=models.CASCADE)
    ticket_class = models.CharField(max_length=20,choices=ENUM, default='econom')


    def __str__(self):
        return f'{self.flight}({self.get_ticket_class_display()})'

