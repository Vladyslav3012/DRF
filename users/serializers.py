from datetime import timedelta

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
import logging
import random
from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import CustomUser


logger = logging.getLogger(__name__)


class CustomUserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    username = serializers.CharField(max_length=50)
    age = serializers.IntegerField(min_value=1, max_value=120,
                                   required=False)
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
            logger.error(f"Email {attrs['email']} has been user")
            raise ValidationError("This email has been used")
        if username_exists:
            logger.error(f"Username {attrs['username']} has been user")
            raise ValidationError("This username has been used")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        otp = random.randint(10000, 99999)
        otp_expire = timezone.now() + timedelta(minutes=5)
        otp_try = 3
        user = CustomUser(
            otp=otp,
            otp_expire=otp_expire,
            otp_try=otp_try,
            **validated_data
        )
        user.set_password(password)
        user.save()

        return user


class UserLogInSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(min_length=8,
                                     max_length=100, write_only=True)


class ActivateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=6)


class RefreshOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8,
                                         max_length=100, write_only=True)
    new_password = serializers.CharField(min_length=8,
                                         max_length=100, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect")
        return value

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        if old_password == new_password:
            raise ValidationError("Passwords must be different")
        return attrs


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)


class SetNewPasswordWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8,
                                         max_length=100, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            logger.info(f"User with {email=} not found")
            raise ValidationError("User with this email not found")

        attrs['user'] = user
        return attrs
