from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

class Airlines(models.Model):
    title = models.CharField(max_length=100)
    detail = models.TextField()
    data_of_create = models.DateField()
    slogan = models.CharField(max_length=200)
    airport = models.ForeignKey("Airports.Airports", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.data_of_create > timezone.now().date():
            raise ValidationError("Час створення не можу бути у майбутньому")

class Airplanes(models.Model):
    model = models.CharField(max_length=100)
    count_of_seats = models.PositiveIntegerField()
    airlines = models.ForeignKey("Airlines", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.model