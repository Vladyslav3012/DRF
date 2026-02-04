from airports.tests.factories import AirportsFactory, CountryFactory
import pytest

from users.tests.factories import UserFactory


URL_AIRPORTS = "/api/v1/country/airport/"


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
