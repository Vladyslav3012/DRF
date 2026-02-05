import pytest
from django.utils.dateparse import parse_datetime

from airplanes.tests.factories import AirplanesFactory
from flights.tests.factories import FlightsFactory
from django.urls import reverse

from users.tests.factories import UserFactory

URL_FLIGHT = reverse('flight-list')


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("regular", 403),
        ("admin", 201),
    ])
def test_crate_flight_permission(api_client, user_type, status):
    if user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)
    elif user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)

    airplanes = AirplanesFactory()
    flight_data = FlightsFactory.build()

    ticket_economy_price = float(flight_data.ticket_economy_price)
    ticket_business_price = float(flight_data.ticket_business_price)
    ticket_first_price = float(flight_data.ticket_first_price)

    ticket_economy = flight_data.tickets_count_economy
    ticket_business = flight_data.tickets_count_business
    ticket_first = flight_data.tickets_count_first

    payload = {
        "flight_status": flight_data.flight_status,
        "city_departure": flight_data.city_departure,
        "city_arrival": flight_data.city_arrival,
        "time_departure": flight_data.time_departure,
        "time_arrival": flight_data.time_arrival,
        "ticket_economy_price": ticket_economy_price,
        "ticket_business_price": ticket_business_price,
        "ticket_first_price": ticket_first_price,
        "tickets_count_economy": ticket_economy,
        "tickets_count_business": ticket_business,
        "tickets_count_first": ticket_first,
        "airplanes": airplanes.model
    }

    response = api_client.post(URL_FLIGHT, data=payload)
    assert response.status_code == status
    if status == 201:
        total_price = sum([ticket_economy_price,
                           ticket_business_price,
                           ticket_first_price])

        assert "id" in response.data
        assert response.data['flight_status'] == flight_data.flight_status
        assert response.data['city_departure'] == flight_data.city_departure
        assert response.data['city_arrival'] == flight_data.city_arrival

        response_departure = parse_datetime(response.data['time_departure'])
        response_arrival = parse_datetime(response.data['time_arrival'])
        assert response_departure == flight_data.time_departure
        assert response_arrival == flight_data.time_arrival

        assert float(response.data['ticket_economy_price']) == ticket_economy_price
        assert float(response.data['ticket_business_price']) == ticket_business_price
        assert float(response.data['ticket_first_price']) == ticket_first_price

        assert response.data['tickets_count_economy'] == ticket_economy
        assert response.data['tickets_count_business'] == ticket_business
        assert response.data['tickets_count_first'] == ticket_first
        assert response.data['airplanes'] == airplanes.model

        assert response.data['total_tickets'] == sum([
            ticket_economy,
            ticket_business,
            ticket_first
        ])

        assert float(response.data['average_price']) == pytest.approx(total_price / 3)


@pytest.mark.django_db
def test_create_flight_invalid_airplane(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    flight_data = FlightsFactory.build()
    payload = {
        "flight_status": flight_data.flight_status,
        "city_departure": flight_data.city_departure,
        "city_arrival": flight_data.city_arrival,
        "time_departure": flight_data.time_departure,
        "time_arrival": flight_data.time_arrival,
        "ticket_economy_price": float(flight_data.ticket_economy_price),
        "ticket_business_price": float(flight_data.ticket_business_price),
        "ticket_first_price": float(flight_data.ticket_first_price),
        "tickets_count_economy": flight_data.tickets_count_economy,
        "tickets_count_business": flight_data.tickets_count_business,
        "tickets_count_first": flight_data.tickets_count_first,
        "airplanes": "NonExistentAirplane"
    }

    response = api_client.post(URL_FLIGHT, data=payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_flights_list(api_client):
    FlightsFactory.create_batch(3)
    response = api_client.get(URL_FLIGHT)
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_flight_retrieve(api_client):
    flight = FlightsFactory()
    response = api_client.get(f"{URL_FLIGHT}{flight.id}/")

    assert response.status_code == 200
    assert response.data["id"] == flight.id
    assert response.data["city_departure"] == flight.city_departure
    assert response.data["city_arrival"] == flight.city_arrival

    assert parse_datetime(response.data["time_departure"]) == flight.time_departure
    assert parse_datetime(response.data["time_arrival"]) == flight.time_arrival

    assert float(response.data["ticket_economy_price"]) == float(flight.ticket_economy_price)
    assert float(response.data["ticket_business_price"]) == float(flight.ticket_business_price)
    assert float(response.data["ticket_first_price"]) == float(flight.ticket_first_price)

    assert response.data["tickets_count_economy"] == flight.tickets_count_economy
    assert response.data["tickets_count_business"] == flight.tickets_count_business
    assert response.data["tickets_count_first"] == flight.tickets_count_first

    assert response.data["airplanes"] == flight.airplanes.model
    assert response.data["total_tickets"] == flight.total_tickets
    assert float(response.data["average_price"]) == pytest.approx(flight.average_price)


@pytest.mark.django_db
def test_update_patch_flight(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    flight = FlightsFactory()
    new_city_departure = "New City Departure"
    payload = {
        "city_departure": new_city_departure
    }

    response = api_client.patch(f"{URL_FLIGHT}{flight.id}/", data=payload)
    assert response.status_code == 200
    assert response.data["city_departure"] == new_city_departure
    assert response.data["city_arrival"] == flight.city_arrival
    assert parse_datetime(response.data["time_departure"]) == flight.time_departure
    assert parse_datetime(response.data["time_arrival"]) == flight.time_arrival
    assert float(response.data["ticket_economy_price"]) == float(flight.ticket_economy_price)
    assert float(response.data["ticket_business_price"]) == float(flight.ticket_business_price)
    assert float(response.data["ticket_first_price"]) == float(flight.ticket_first_price)
    assert response.data["airplanes"] == flight.airplanes.model
    assert response.data["total_tickets"] == flight.total_tickets
    assert float(response.data["average_price"]) == pytest.approx(flight.average_price)


@pytest.mark.django_db
def test_update_put_flight(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    flight = FlightsFactory()
    new_city_departure = "Updated City Departure"
    new_city_arrival = "Updated City Arrival"
    payload = {
        "flight_status": flight.flight_status,
        "city_departure": new_city_departure,
        "city_arrival": new_city_arrival,
        "time_departure": flight.time_departure,
        "time_arrival": flight.time_arrival,
        "ticket_economy_price": float(flight.ticket_economy_price),
        "ticket_business_price": float(flight.ticket_business_price),
        "ticket_first_price": float(flight.ticket_first_price),
        "tickets_count_economy": flight.tickets_count_economy,
        "tickets_count_business": flight.tickets_count_business,
        "tickets_count_first": flight.tickets_count_first,
        "airplanes": flight.airplanes.model
    }

    response = api_client.put(f"{URL_FLIGHT}{flight.id}/", data=payload)

    assert response.status_code == 200
    assert response.data["city_departure"] == new_city_departure
    assert response.data["city_arrival"] == new_city_arrival

    assert parse_datetime(response.data["time_departure"]) == flight.time_departure
    assert parse_datetime(response.data["time_arrival"]) == flight.time_arrival

    assert float(response.data["ticket_economy_price"]) == float(flight.ticket_economy_price)
    assert float(response.data["ticket_business_price"]) == float(flight.ticket_business_price)
    assert float(response.data["ticket_first_price"]) == float(flight.ticket_first_price)

    assert response.data["airplanes"] == flight.airplanes.model
    assert response.data["total_tickets"] == flight.total_tickets

    assert float(response.data["average_price"]) == pytest.approx(flight.average_price)


@pytest.mark.django_db
def test_delete_flight(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    flight = FlightsFactory()
    response = api_client.delete(f"{URL_FLIGHT}{flight.id}/")
    assert response.status_code == 204
    get_response = api_client.get(f"{URL_FLIGHT}{flight.id}/")
    assert get_response.status_code == 404
