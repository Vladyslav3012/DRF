import logging
from collections import Counter

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import transaction, models
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from flights.models import Flights
from .models import Order
from .serializer import OrderCreateSerializer, OrderSerializer, OrderSerializerForUpdate, PaymentSerializer
from .service import stripe_session_check, expire_session, webhook_check


logger = logging.getLogger(__name__)


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
        )  # --> {(1, 'economy'): 2, (2, 'business'): 1}
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

        return Response({
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
