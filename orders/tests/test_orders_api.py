import pytest

from flights.tests.factories import TicketFactory, FlightsFactory
from orders.tests.factories import OrderFactory
from django.urls import reverse
from users.tests.factories import UserFactory


URL_ORDERS = reverse('orders')


@pytest.mark.django_db
def test_order_total_price(api_client):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)

    flight = FlightsFactory(
        ticket_economy_price=100.00,
        ticket_business_price=200.00
    )

    order = OrderFactory(owner=user)
    TicketFactory(order=order, flight=flight, ticket_class='economy')
    TicketFactory(order=order, flight=flight, ticket_class='economy')
    TicketFactory(order=order, flight=flight, ticket_class='business')

    assert order.total_price == 400.00


@pytest.mark.django_db
def test_order_creation(api_client):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)

    flight = FlightsFactory(
        ticket_economy_price=100.00,
        ticket_business_price=200.00
    )

    payload = {
        "currency": "usd",
        "tickets": [
            {"flight": flight.id, "ticket_class": "economy", "seat_number": 1},
            {"flight": flight.id, "ticket_class": "business", "seat_number": 2},
        ]
    }

    response = api_client.post(URL_ORDERS, data=payload, format='json')
    assert response.status_code == 201
    ticket_data = response.data['tickets']
    assert len(ticket_data) == 2
    assert ticket_data[0]['ticket_class'] == 'economy'
    assert ticket_data[1]['ticket_class'] == 'business'
    assert response.data['currency'] == "usd"
    assert response.data['status'] == "Pending"
    assert response.data['quantity'] == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("regular", 403),
        ("admin", 200),
    ],)
def test_update_order_permission(api_client, user_type, status):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)

    flight = FlightsFactory(
        ticket_economy_price=100.00,
        ticket_business_price=200.00
    )

    payload_post = {
        "currency": "usd",
        "tickets": [
            {"flight": flight.id, "ticket_class": "economy", "seat_number": 1},
            {"flight": flight.id, "ticket_class": "business", "seat_number": 2},
        ]
    }
    response_post = api_client.post(URL_ORDERS, data=payload_post, format='json')
    assert response_post.status_code == 201
    assert "order_id" in response_post.data
    order_id = response_post.data['order_id']

    if user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)
    elif user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)
    elif user_type == "anonymous":
        api_client.force_authenticate(user=None)

    payload_patch = {
        "status": "Confirmed"
    }

    response = api_client.patch(f"{URL_ORDERS}{order_id}/", data=payload_patch)
    assert response.status_code == status
    if status == 200:
        assert response.data['status'] == "Confirmed"
        assert response.data['order_id'] == str(order_id)
