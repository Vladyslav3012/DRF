import pytest
from airports.tests.factories import CountryFactory
from users.tests.factories import UserFactory
from django.urls import reverse


URL_COUNTRY = reverse('country-list')


"""
TESTING COUNTRY CREATION PERMISSIONS
"""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("regular", 403),
        ("admin", 201),
    ],)
def test_create_country_permission(api_client, user_type, status):
    if user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)
    elif user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)

    country_data = CountryFactory.build()
    payload = {
        "title": country_data.title,
        "capital": country_data.capital,
    }
    response = api_client.post(URL_COUNTRY, data=payload)
    assert response.status_code == status
    if status == 201:
        assert response.data['title'] == country_data.title
        assert response.data['capital'] == country_data.capital


@pytest.mark.django_db
def test_create_country_existing_title(auth_admin):

    existing_country = CountryFactory()
    country_data = CountryFactory.build(title=existing_country.title)
    payload = {
        "title": country_data.title,
        "capital": country_data.capital,
    }
    response = auth_admin.post(URL_COUNTRY, data=payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_country_list(api_client):
    CountryFactory.create_batch(3)
    response = api_client.get(URL_COUNTRY)
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_country_retrieve(api_client):
    country = CountryFactory()
    response = api_client.get(f"{URL_COUNTRY}{country.id}/")
    assert response.status_code == 200
    assert response.data["id"] == country.id
    assert response.data["title"] == country.title
    assert response.data["capital"] == country.capital


@pytest.mark.django_db
def test_update_country(auth_admin):

    country = CountryFactory()
    payload = {
        "title": "UpdatedCountry",
        "capital": "UpdatedCapital"
    }
    response = auth_admin.put(f"{URL_COUNTRY}{country.id}/", data=payload)
    assert response.status_code == 200
    assert response.data["title"] == "UpdatedCountry"
    assert response.data["capital"] == "UpdatedCapital"


@pytest.mark.django_db
def test_delete_country(auth_admin):

    country = CountryFactory()
    response = auth_admin.delete(f"{URL_COUNTRY}{country.id}/")
    assert response.status_code == 204
    get_response = auth_admin.get(f"{URL_COUNTRY}{country.id}/")
    assert get_response.status_code == 404
