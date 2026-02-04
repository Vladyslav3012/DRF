import pytest
from airplanes.tests.factories import AirlinesFactory, AirplanesFactory
from airports.tests.factories import AirportsFactory
from users.tests.factories import UserFactory

URL_AIRLINES = "/api/v1/airlines/"
URL_AIRPLANES = '/api/v1/airplanes/'


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, status",
    [
        ("anonymous", 401),
        ("admin", 201),
        ("regular", 403),
],)
def test_create_airlines_permission(api_client, user_type, status):
    if user_type == "admin":
        admin = UserFactory(is_staff=True)
        api_client.force_authenticate(user=admin)
    elif user_type == "regular":
        user = UserFactory()
        api_client.force_authenticate(user=user)

    airports = AirportsFactory()
    airlines_data = AirlinesFactory.build()
    payload = {
        "title": airlines_data.title,
        "detail": airlines_data.detail,
        "data_of_create": airlines_data.data_of_create,
        "slogan": airlines_data.slogan,
        "airport": airports.title,
    }

    response = api_client.post(URL_AIRLINES, data=payload)

    assert response.status_code == status
    if status == 201:
        assert "id" in response.data
        assert response.data['title'] == airlines_data.title
        assert response.data['detail'] == airlines_data.detail
        assert response.data['data_of_create'] == airlines_data.data_of_create
        assert response.data['slogan'] == airlines_data.slogan
        assert response.data['airport'] == airports.title



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
