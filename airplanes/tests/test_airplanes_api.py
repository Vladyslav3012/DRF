import pytest
from airplanes.tests.factories import AirlinesFactory, AirplanesFactory
from users.tests.factories import UserFactory
from django.urls import reverse


URL_AIRPLANES = reverse('airplanes-list')


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("admin", 201),
        ("regular", 403),
    ],)
def test_create_airplanes_permission(api_client, user_type, status):
    if user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)
    elif user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)

    airline = AirlinesFactory()
    airplane_data = AirplanesFactory.build()

    payload = {
        "model": airplane_data.model,
        "economy_class_seats": airplane_data.economy_class_seats,
        "business_class_seats": airplane_data.business_class_seats,
        "first_class_seats": airplane_data.first_class_seats,
        "airlines": airline.title,
    }

    response = api_client.post(URL_AIRPLANES, data=payload)

    assert response.status_code == status
    if status == 201:
        economy_seats = airplane_data.economy_class_seats
        business_seats = airplane_data.business_class_seats
        first_seats = airplane_data.first_class_seats

        assert response.data["model"] == airplane_data.model
        assert response.data["economy_class_seats"] == economy_seats
        assert response.data["business_class_seats"] == business_seats
        assert response.data["first_class_seats"] == first_seats
        assert response.data["airlines"] == airline.title

        assert "total_seats" in response.data
        total_seats = sum([economy_seats, business_seats, first_seats])
        assert response.data["total_seats"] == total_seats


@pytest.mark.django_db
def test_get_airplanes_list(api_client):
    AirplanesFactory.create_batch(3)
    response = api_client.get(URL_AIRPLANES)
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_airplanes_retrieve(api_client):
    airplane = AirplanesFactory()
    response = api_client.get(f"{URL_AIRPLANES}{airplane.id}/")
    assert response.status_code == 200
    assert response.data["model"] == airplane.model
    assert response.data["economy_class_seats"] == airplane.economy_class_seats
    assert response.data["business_class_seats"] == airplane.business_class_seats
    assert response.data["first_class_seats"] == airplane.first_class_seats
    assert response.data["total_seats"] == airplane.total_seats
    assert response.data["airlines"] == airplane.airlines.title
    assert "flights" in response.data
    assert len(response.data["flights"]) == airplane.flights.count()