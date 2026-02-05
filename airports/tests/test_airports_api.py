from airports.tests.factories import AirportsFactory, CountryFactory
import pytest
from django.urls import reverse
from users.tests.factories import UserFactory


URL_AIRPORTS = reverse('airport-list')


"""
TESTING AIRPORT CREATION PERMISSIONS
"""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("regular", 403),
        ("admin", 201),
    ],)
def test_create_airport_permission(api_client, user_type, status):
    if user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)
    elif user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)

    country = CountryFactory()
    airport_data = AirportsFactory.build()
    payload = {
        "title": airport_data.title,
        "address": airport_data.address,
        "contact": airport_data.contact,
        "country": country.title,
    }
    response = api_client.post(URL_AIRPORTS, data=payload)
    assert response.status_code == status
    if status == 201:
        assert "id" in response.data
        assert response.data['title'] == airport_data.title
        assert response.data['address'] == airport_data.address
        assert response.data['contact'] == airport_data.contact
        assert response.data['country'] == country.title


"""
TESTING AIRPORT CREATION WITH INVALID COUNTRY
"""


@pytest.mark.django_db
def test_create_airport_invalid_country(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    airport_data = AirportsFactory.build()
    payload = {
        "title": airport_data.title,
        "address": airport_data.address,
        "contact": airport_data.contact,
        "country": "NonExistentCountry",
    }
    response = api_client.post(URL_AIRPORTS, data=payload)
    assert response.status_code == 400


"""
TESTING EXISTING AIRPORT CREATING
"""


@pytest.mark.django_db
def test_create_existing_airport(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    country = CountryFactory()

    existing_airport = AirportsFactory(country=country)
    payload = {
        "title": existing_airport.title,
        "address": existing_airport.address,
        "contact": existing_airport.contact,
        "country": country.title,
    }
    response = api_client.post(URL_AIRPORTS, data=payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_airports_list(api_client):
    AirportsFactory.create_batch(3)
    response = api_client.get(URL_AIRPORTS)
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_airports_retrieve(api_client):
    airport = AirportsFactory()
    response = api_client.get(f"{URL_AIRPORTS}{airport.id}/")
    assert response.status_code == 200
    assert response.data["id"] == airport.id
    assert response.data["title"] == airport.title
    assert response.data["address"] == airport.address
    assert response.data["contact"] == airport.contact
    assert response.data["country"] == airport.country.title


@pytest.mark.django_db
def test_update_airport(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    airport = AirportsFactory()
    country = CountryFactory()
    payload = {
        "title": "UpdatedAirport",
        "address": "UpdatedAddress",
        "contact": "UpdatedContact",
        "country": country.title,
    }
    response = api_client.put(f"{URL_AIRPORTS}{airport.id}/", data=payload)
    assert response.status_code == 200
    assert response.data["title"] == "UpdatedAirport"
    assert response.data["address"] == "UpdatedAddress"
    assert response.data["contact"] == "UpdatedContact"
    assert response.data["country"] == country.title


@pytest.mark.django_db
def test_delete_airport(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    airport = AirportsFactory()
    response = api_client.delete(f"{URL_AIRPORTS}{airport.id}/")
    assert response.status_code == 204
    get_response = api_client.get(f"{URL_AIRPORTS}{airport.id}/")
    assert get_response.status_code == 404
