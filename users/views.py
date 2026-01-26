import logging
from collections import Counter
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.db import transaction, models
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import Order
from .serializers import (CustomUserRegisterSerializer, UserLogInSerializer,
                          OrderSerializer, OrderCreateSerializer, OrderSerializerForUpdate,
                          PaymentSerializer)
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


@extend_schema(tags=['Users'])
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


@extend_schema(tags=['Users'])
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


@extend_schema(tags=['Orders'])
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

        tickets_by_class = Counter(
            (ticket["flight"].id, ticket["ticket_class"]) for ticket in tickets
        ) # --> {(1, 'economy'): 2, (2, 'business'): 1}
        # {(flight_id, ticket class) : count},

        logger.info(f"Create tickets: {tickets_by_class}")

        for (flight_id, ticket_class), count in tickets_by_class.items():
            flight = (
                Flights.objects
                .select_for_update()
                .get(pk=flight_id)
            )

            if ticket_class == "economy":
                if count > flight.tickets_count_economy:
                    logger.error("Not enough economy seats")
                    raise ValidationError("Not enough economy class seats")
                flight.tickets_count_economy = models.F('tickets_count_economy') - count
                flight.save(update_fields=["tickets_count_economy"])
                logger.info(f"On flight {flight_id}, buying {count} ticket"
                            f" from {ticket_class} class")

            elif ticket_class == "business":
                if count > flight.tickets_count_business:
                    logger.error("Not enough business seats")
                    raise ValidationError("Not enough business class seats")
                flight.tickets_count_business = models.F('tickets_count_business') - count
                flight.save(update_fields=["tickets_count_business"])
                logger.info(f"On flight {flight_id}, buying {count} ticket"
                            f" from {ticket_class} class")

            elif ticket_class == "first":
                if count > flight.tickets_count_first:
                    logger.error("Not enough first class seats")
                    raise ValidationError("Not enough first class seats")
                flight.tickets_count_first = models.F('tickets_count_first') - count
                flight.save(update_fields=["tickets_count_first"])
                logger.info(f"On flight {flight_id}, buying {count} ticket "
                            f"from {ticket_class} class")

            else:
                logger.error(f"Unknow ticket class {ticket_class}")
                raise ValidationError("Unknow ticket class")

        serializer.save(owner=self.request.user)


@extend_schema(tags=['Orders'])
class OrderUpdateApiView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializerForUpdate


@extend_schema(tags=['Stripe'])
class StripeApiView(generics.GenericAPIView):
    def post(self, request: Request, order_id):
        status_order = ("Confirmed", "Expired")

        try:
            order = Order.objects.prefetch_related(
                "tickets",
                "payments"
            ).get(order_id=order_id, owner=request.user)
        except Exception:
            logger.error(f"Order #{order_id} not found, or you are not its owner")
            raise ValidationError("Order not found, or you are not its owner")

        if order.status in status_order:
            logger.error(f"This order has already been paid or expired {order_id}")
            raise ValidationError("This order has already been paid or expired")

        check_session, payment = stripe_session_check(order=order, user=request.user)
        #use func from .service, she has all the logic

        return Response({
        "checkout_url": check_session.url,
        "payment": PaymentSerializer(payment).data
        })


@extend_schema(tags=['Stripe'])
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, token):
        return webhook_check(request=request, token=token)
        #called func from service


@extend_schema(tags=['Stripe'])
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

