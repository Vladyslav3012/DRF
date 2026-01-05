from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

class Airlines(models.Model):
    title = models.CharField(max_length=100, unique=True)
    detail = models.TextField()
    data_of_create = models.DateField(auto_now_add=True)
    slogan = models.CharField(max_length=200)
    airport = models.ForeignKey("airports.airports",
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="airlines")

    def __str__(self):
        return self.title

    def clean(self):
        if self.data_of_create > timezone.now().date():
            raise ValidationError("Час створення не можу бути у майбутньому")


class Airplanes(models.Model):
    model = models.CharField(max_length=100, unique=True)
    count_of_seats = models.PositiveSmallIntegerField()
    airlines = models.ForeignKey("Airlines",
                                 on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name="airplanes")

    def __str__(self):
        return self.model