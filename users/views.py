import logging
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
                          OrderSerializer, OrderCreateSerializer,
                          OrderSerializerForUpdate, PaymentSerializer)
from rest_framework.response import Response
from rest_framework.request import Request
from flights.models import Flights

from .service import stripe_session_check, webhook_check, expire_session

User = get_user_model()

logger = logging.getLogger(__name__)


def get_user_token(user: User):
    refresh = RefreshToken.for_user(user)
    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
    return tokens


class SignUpView(generics.GenericAPIView):
    serializer_class = CustomUserRegisterSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Success sing up {serializer.validated_data.get('email')}")
        return Response({"msg": "SingUp success",
                         "Data": serializer.data})


class LogInView(APIView):
    permission_classes = []

    @extend_schema(request=UserLogInSerializer)
    def post(self, request: Request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_user_token(user)
            logger.info(f"Success LogIn {user}")
            return Response({"msg": "LoginSuccessful",
                             "token": token})
        logger.error(f"Invalid data to authenticate {email}")
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
        logger.info(f"Create tickets: {tickets_by_class}")

        flight = (
            Flights.objects
            .select_for_update()
            .get(pk=flight.pk)
        )

        if tickets_by_class.get("economy", 0) > flight.tickets_count_economy:
            logger.error("Not enough economy seats")
            raise ValidationError("Not enough economy class seats")


        if tickets_by_class.get("business", 0) > flight.tickets_count_business:
            logger.error("Not enough business seats")
            raise ValidationError("Not enough business class seats")

        if tickets_by_class.get("first", 0) > flight.tickets_count_first:
            logger.error("Not enough first class seats")
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
        status_order = ("Confirmed", "Expired")

        try:
            order = Order.objects.prefetch_related(
            "tickets"
            ).get(order_id=order_id, owner=request.user)
        except Exception:
            logger.error(f"Order #{order_id} not found, or you are not its owner",
                         extra={"order_id to search": order_id,
                                "owner to search": request.user})

            raise ValidationError("Order not found, or you are not its owner")
        if order.status in status_order:
            logger.error(f"This order has already been paid or expired {order_id}")
            raise ValidationError("This order has already been paid or expired")
        #get order from database by order id,
        #and check whether owner=request.user

        check_session, payment = stripe_session_check(order=order, user=request.user)
        #use func from .service, she has all the logic
        logger.info(f"Create stripe check-session #{check_session.id}",
                    extra={"order_id": order_id,
                    "payment": payment}
                    )

        order.stripe_checkout_session = check_session.id
        order.save()
        #save order with new session id

        return Response({
        "checkout_url": check_session.url,
        "payment": PaymentSerializer(payment).data
        })


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        return webhook_check(request=request)
        #called func from service


@method_decorator(csrf_exempt, name="dispatch")
class WebhookExpireApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Exception:
            logger.error(f"Order with order_id {order_id} not found")
            raise ValidationError("Order not found")

        if order.status == "Confirmed":
            logger.error("This order has already been paid")
            raise ValidationError("This order has already been paid")

        logger.info(f"Order #{order_id} expired")
        return expire_session(request=request, order=order)

def success(request):
    return JsonResponse({"msg": "success"})


def cancel(request):
    return JsonResponse({"msg": "cancel"})
