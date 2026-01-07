from django.db import models

class Country(models.Model):
    title = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100)


    def __str__(self):
        return self.title


class Airports(models.Model):
    title = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="airports"
    )


    def __str__(self):
        return self.title
