import pytest
from airports.tests.factories import CountryFactory
from users.tests.factories import UserFactory


URL_COUNTRY = "/api/v1/country/"


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