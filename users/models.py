import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser has to have is_staff true")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser has to have is_superuser true")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.CharField(max_length=80, unique=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "age"]

    def __str__(self):
        return self.username


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING = "Pending", "Pending"
        CONFIRMED = "Confirmed", "Confirmed"
        CANCELLED = "Cancelled", "Cancelled"

    class CurrencyChoice(models.TextChoices):
        USD = "usd", "USD"
        UAH = "uah", "UAH"
        EURO = "eur", "EUR"

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
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
