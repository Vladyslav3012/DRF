from rest_framework import serializers
from rest_framework.validators import ValidationError
from flights.models import Ticket
from .models import CustomUser
from rest_framework.authtoken.models import Token


class CustomUserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    username = serializers.CharField(max_length=50)
    age = serializers.IntegerField(min_value=1, max_value=120)
    password = serializers.CharField(min_length=8,
                                     write_only=True,
                                     max_length=50)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "age"]

    def validate(self, attrs):
        email_exists = CustomUser.objects.filter(email=attrs['email']).exists()
        username_exists = CustomUser.objects.filter(username=attrs['username']).exists()
        if email_exists:
            raise ValidationError("This email has been used")
        if username_exists:
            raise ValidationError("This username has been used")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        Token.objects.get_or_create(user=user)
        return user


class UserLogInSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
