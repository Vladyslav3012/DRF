from collections import Counter
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import Order
from .serializers import (CustomUserRegisterSerializer, UserLogInSerializer,
                          OrderSerializer, OrderCreateSerializer, OrderSerializerForUpdate)
from rest_framework.response import Response
from rest_framework.request import Request
from flights.models import Flights

from .service import stripe_session_check, webhook_check


User = get_user_model()


def get_user_token(user: User):
    refresh = RefreshToken.for_user(user)
    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
    return tokens


class SignUpView(generics.GenericAPIView):
    serializer_class = CustomUserRegisterSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"msg": "User create successful", "data": serializer.data})
        return Response(serializer.errors)


class LogInView(APIView):
    permission_classes = []

    @extend_schema(request=UserLogInSerializer)
    def post(self, request: Request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_user_token(user)
            return Response({"msg": "LoginSuccessful",
                             "token": token})
        return Response(data={"msg": "Invalid email or password"})

    def get(self, request: Request):
        content = {
            "user": str(request.user),
            "auth": str(request.auth)
        }
        return Response(data=content)


class OrderListCreateApiView(generics.ListCreateAPIView):

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user).prefetch_related(
            'tickets',
            'tickets__flight'
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        tickets = serializer.validated_data["tickets"]
        flight = tickets[0]["flight"]

        tickets_by_class = Counter(
            ticket["ticket_class"] for ticket in tickets
        ) # --> {"economy": 1, "business": 1}

        flight = (
            Flights.objects
            .select_for_update()
            .get(pk=flight.pk)
        )

        if tickets_by_class.get("economy", 0) > flight.tickets_count_economy:
            raise ValidationError("Not enough economy seats")

        if tickets_by_class.get("business", 0) > flight.tickets_count_business:
            raise ValidationError("Not enough business seats")

        if tickets_by_class.get("first", 0) > flight.tickets_count_first:
            raise ValidationError("Not enough first class seats")

        flight.tickets_count_economy -= tickets_by_class.get("economy", 0)
        flight.tickets_count_business -= tickets_by_class.get("business", 0)
        flight.tickets_count_first -= tickets_by_class.get("first", 0)
        flight.save()

        serializer.save(owner=self.request.user)


class OrderUpdateApiView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializerForUpdate


class StripeApiView(generics.GenericAPIView):
    def post(self, request: Request, order_id):
        order = Order.objects.prefetch_related(
            "tickets"
        ).get(order_id=order_id, owner=request.user)
        #get order from database by order id,
        #and check whether owner=request.user

        check_session = stripe_session_check(order=order, user_id=request.user.id)
        #use func from .service, she has all the logic

        order.stripe_checkout_session = check_session.id
        order.save()
        #save order with new session id

        return Response({
            "checkout_url": check_session.url
        })


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        return webhook_check(request=request)
        #called func from service


def success(request):
    return JsonResponse({"msg": "success"})


def cancel(request):
    return JsonResponse({"msg": "cancel"})
