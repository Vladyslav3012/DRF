from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from flights.models import Ticket
from .models import CustomUser


# class CustomUserSerializer(UserCreateSerializer):
#     ticket = serializers.StringRelatedField(many=True)
#     class Meta:
#         model = CustomUser
#         fields = ["id", "username", "email", "password", "age", "ticket"]