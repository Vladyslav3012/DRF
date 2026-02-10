import logging
import random
from datetime import timedelta
import socket

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import CustomUser
from .serializers import (CustomUserRegisterSerializer, UserLogInSerializer,
                          ActivateUserSerializer, ChangePasswordSerializer,
                          RequestPasswordResetSerializer, SetNewPasswordWithOTPSerializer, RefreshOTPSerializer)
from rest_framework.response import Response
from rest_framework.request import Request
from .tasks import send_email_task


User = get_user_model()

logger = logging.getLogger(__name__)


def get_user_token(user: User):
    refresh = RefreshToken.for_user(user)
    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
    return tokens


@extend_schema(tags=['Auth'])
class SignUpView(generics.GenericAPIView):
    serializer_class = CustomUserRegisterSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Success sing up {serializer.validated_data.get('email')}")
        return Response({"msg": "SingUp success",
                         "data": serializer.data}, status=201)


@extend_schema(tags=['Users'])
class ActivateUserApiView(generics.GenericAPIView):
    serializer_class = ActivateUserSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data.get('email')

        user = get_object_or_404(CustomUser, email=email)

        logger.info(f"Email {email} ask a new code to activate")

        if user.is_active:
            return Response({"msg": "User is already active"}, status=400)

        otp_get = serializer.validated_data.get('otp')

        user = get_object_or_404(CustomUser, email=email)

        otp_in_db = user.otp
        otp_expire = user.otp_expire

        if user.otp_try <= 0:
            return Response({"msg": "You have no more attempts."
                                    " Please request a new code"},
                            status=400)

        if otp_expire < timezone.now():
            return Response({"msg": "You code expired. "
                                    "Please request a new code"},
                            status=400)

        if otp_get == otp_in_db:
            user.is_active = True
            user.otp_expire = None
            user.otp_try = None
            user.otp = None
            user.save(update_fields=['is_active', 'otp_expire',
                                     'otp_try', 'otp'])
            logger.info(f"Success activated email {email}")
            return Response({"msg": "Success, you confirmed you email"})

        user.otp_try -= 1
        user.save(update_fields=['otp_try'])
        return Response({"msg": f"You send incorrect code "
                                f"please try again, try left: {user.otp_try}"},
                        status=400)


@extend_schema(tags=['Users'])
class RefreshOTPApiView(generics.GenericAPIView):
    serializer_class = RefreshOTPSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = get_object_or_404(CustomUser, email=email)

        if user.is_active:
            return Response({"msg": "User is already active"}, status=400)

        if user and user.check_password(password):

            otp = random.randint(10000, 99999)
            otp_expire = timezone.now() + timedelta(minutes=5)

            user.otp = otp
            user.otp_expire = otp_expire
            user.otp_try = 3

            user.save(update_fields=['otp', 'otp_expire', 'otp_try'])

            subject = "Your gmail has been register on our website"
            message = (f"Hello {user.username}. {subject}, nice to meet you!\n"
                       f"You code to activate email: {otp}, "
                       f"you have 5 min to activate")
            to_email = user.email

            send_email_task.delay_on_commit(subject, message, [to_email])
            return Response({"msg": "New code send to you email"})
        return Response({"msg": "Invalid email or password"}, status=400)


@extend_schema(tags=['Auth'])
class LogInView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = UserLogInSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_user_token(user)
            logger.info(f"Success LogIn {user}")
            return Response({"msg": "LoginSuccessful",
                             "token": token})
        logger.error(f"Invalid data to authenticate {email}")
        return Response(data={"msg": "Invalid email or password"}, status=401)

    def get(self, request: Request):
        if self.request.user.is_anonymous:
            return Response({"msg": "You are not authenticated"}, status=401)
        content = {
            "username": str(request.user),
            "email": str(request.user.email),
            "auth": str(request.auth)
        }
        return Response(data=content)


@extend_schema(tags=['Users'])
class ChangePasswordApiView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request: Request):
        user = request.user
        logger.info(f"User: {user}, ask to change password")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.info(f"User: {user}, got validate error"
                        f" {serializer.errors}")
            return Response(serializer.errors, status=400)

        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        logger.info(f"User: {user}, change password success")
        return Response("Password change success", status=200)


@extend_schema(tags=['Users'])
class ChangePasswordRequestOTP(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data.get('email')

        user = get_object_or_404(CustomUser, email=email)

        otp = random.randint(10000, 99999)
        if not user:
            logger.info(f"User with {email=} not found")
            raise ValidationError("User with this email not found")
        user.otp = otp
        user.otp_expire = timezone.now() + timedelta(minutes=5)
        user.otp_try = 3
        user.save(update_fields=['otp', 'otp_expire',
                                 'otp_try'])

        subject = "Password Reset Request"
        message = (f"A password change request has been sent to with email. \n"
                   f"If you are not asking about this, please ignore this email. \n"
                   f"Your code to reset password: {otp}")
        recipient_list = [email]
        send_email_task.delay_on_commit(subject, message, recipient_list)

        logger.info(f"Sending OTP code for reset password to {user.username=}")
        return Response({"msg": "We have sent a secret code to your email address."})


@extend_schema(tags=["Users"])
class SetNewPasswordWithOTP(generics.GenericAPIView):
    serializer_class = SetNewPasswordWithOTPSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data.get('user')
        new_password = serializer.validated_data.get('new_password')
        otp_get = serializer.validated_data.get('otp')

        otp_in_db = user.otp
        otp_expire = user.otp_expire

        if otp_in_db is None:
            return Response({"msg": "You don`t ask code to you email"})

        if user.otp_try <= 0:
            return Response({"msg": "You have no more attempts."
                                    " Please request a new code"},
                            status=400)

        if otp_expire < timezone.now():
            return Response({"msg": "You code expired. "
                                    "Please request a new code"},
                            status=400)

        if otp_get == otp_in_db:
            user.set_password(new_password)
            user.otp_expire = None
            user.otp_try = None
            user.otp = None
            user.save()
            logger.info(f"{user.username=} change password with OTP")
            return Response({"msg": "Success, you change your password"})

        user.otp_try -= 1
        user.save(update_fields=['otp_try'])
        return Response({"msg": f"You send incorrect code, "
                                f"please try again, try left: {user.otp_try}"})


def test_email_view(request):
    output = []
    output.append("<h2>🛠️ Email Debugger</h2>")

    # 1. Перевірка налаштувань
    output.append(f"<b>Host:</b> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}<br>")
    output.append(f"<b>User:</b> {settings.EMAIL_HOST_USER}<br>")
    output.append(f"<b>TLS/SSL:</b> {settings.EMAIL_USE_TLS} / {settings.EMAIL_USE_SSL}<br>")

    # 2. Перевірка DNS (чи працює патч IPv4)
    try:
        ip = socket.gethostbyname('smtp.gmail.com')
        output.append(f"<b>✅ DNS Resolve:</b> {ip} (IPv4)<br>")
    except Exception as e:
        output.append(f"<b>❌ DNS Error:</b> {e}<br>")

    # 3. Спроба відправки
    try:
        send_mail(
            'Render Test',
            'Hello! This is a test from Render via standard Django view.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Відправляємо самі собі
            fail_silently=False,
        )
        output.append("<h3>✅ SUCCESS! Email sent.</h3>")
    except Exception as e:
        output.append(f"<h3>❌ ERROR: {e}</h3>")
        output.append(f"<pre>{str(e)}</pre>")

    return HttpResponse("".join(output))