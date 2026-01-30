import logging

from flights.models import Ticket
from flights.serializers import TicketCreateSerializer
from .models import Payment, Order
from users.models import CustomUser
from rest_framework import serializers


logger = logging.getLogger(__name__)


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    tickets = serializers.StringRelatedField(read_only=True, many=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    quantity = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(Order.StatusChoice.choices,
                                     default=Order.StatusChoice.PENDING,
                                     read_only=True)
    currency = serializers.ChoiceField(Order.CurrencyChoice.choices,
                                       default=Order.CurrencyChoice.USD)

    class Meta:
        model = Order
        fields = ['order_id', 'owner', 'status',
                  'created_at', 'tickets', 'total_price',
                  'currency', 'quantity']


class OrderCreateSerializer(OrderSerializer):
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'tickets', 'owner', 'status',
                  'created_at',
                  'currency', 'quantity']

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(
            quantity=len(tickets_data),
            **validated_data
        )
        logger.info(f"Create order #{order.order_id}")

        for ticket in tickets_data:
            tick = Ticket.objects.create(order=order, **ticket)
            logger.info(f"Create ticket #{tick.id}")
        return order


class OrderSerializerForUpdate(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    tickets = serializers.StringRelatedField(read_only=True, many=True)
    owner = serializers.SlugRelatedField(slug_field="username",
                                         queryset=CustomUser.objects.all())
    quantity = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(Order.StatusChoice.choices,
                                     default=Order.StatusChoice.PENDING)
    currency = serializers.ChoiceField(Order.CurrencyChoice.choices,
                                       default=Order.CurrencyChoice.USD)

    class Meta:
        model = Order
        fields = ['order_id', 'tickets', 'owner', 'status',
                  'created_at',
                  'currency', 'quantity']


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(
        slug_field="order_id",
        queryset=Order.objects.all()
    )
    owner = serializers.SlugRelatedField(slug_field="username",
                                         queryset=CustomUser.objects.all())

    class Meta:
        model = Payment
        fields = ['payment_id', 'order', 'owner', 'status_payment',
                  'price', 'currency', 'created_at', 'payed_at', 'checkout_url',
                  'session_expires_at'
                  ]
