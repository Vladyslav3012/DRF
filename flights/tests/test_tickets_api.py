import pytest
from django.urls import reverse
from users.tests.factories import UserFactory
from flights.tests.factories import FlightsFactory, TicketFactory


URL_TICKETS = reverse('ticket-list')


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("regular", 200),
    ])
def test_get_tickets_permission(api_client, user_type, status):
    flight = FlightsFactory()
    if user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)
        TicketFactory.create_batch(3, flight=flight, owner=user)

    else:
        TicketFactory.create_batch(3, flight=flight)

    response = api_client.get(URL_TICKETS)
    assert response.status_code == status
    if status == 200:
        assert len(response.data) == 3
        for ticket_data in response.data:
            assert "id" in ticket_data
            assert "ticket_class" in ticket_data
            assert "seat_number" in ticket_data
            assert "flight" in ticket_data
