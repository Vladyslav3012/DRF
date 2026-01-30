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
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser has to have is_staff true")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser has to have is_superuser true")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.CharField(max_length=80, unique=True)
    age = models.PositiveIntegerField(blank=True,
                                      null=True)
    otp = models.CharField(max_length=6, blank=True,
                           null=True)
    otp_expire = models.DateTimeField(blank=True, null=True)
    otp_try = models.PositiveSmallIntegerField(blank=True,
                                               null=True)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "age"]

    def __str__(self):
        return self.username
