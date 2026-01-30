from django.db import models
from django.core.exceptions import ValidationError


class Airlines(models.Model):
    title = models.CharField(max_length=100, unique=True)
    detail = models.TextField()
    data_of_create = models.DateField()
    slogan = models.CharField(max_length=200)
    airport = models.ForeignKey("airports.airports",
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="airlines")

    def __str__(self):
        return self.title


class Airplanes(models.Model):
    model = models.CharField(max_length=100)
    economy_class_seats = models.PositiveSmallIntegerField(default=0)
    business_class_seats = models.PositiveSmallIntegerField(default=0)
    first_class_seats = models.PositiveSmallIntegerField(default=0)
    airlines = models.ForeignKey("Airlines",
                                 on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name="airplanes")

    @property
    def total_seats(self):
        return sum([self.economy_class_seats,
                    self.first_class_seats,
                    self.business_class_seats])

    def clean(self):
        if self.total_seats == 0:
            raise ValidationError("Airplane must have at least one seat")

    def __str__(self):
        return f'{self.model} with {self.total_seats} seats'
