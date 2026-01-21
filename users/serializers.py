import logging

from rest_framework import serializers
from rest_framework.validators import ValidationError

from flights.models import Ticket
from flights.serializers import TicketCreateSerializer
from .models import CustomUser, Order, Payment
from rest_framework.authtoken.models import Token


logger = logging.getLogger(__name__)


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
            logger.error(f"Email {attrs['email']} has been user")
            raise ValidationError("This email has been used")
        if username_exists:
            logger.error(f"Username {attrs['username']} has been user")
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
    password = serializers.CharField(min_length=8,
                                     max_length=100, write_only=True)


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
