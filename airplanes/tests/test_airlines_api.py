import pytest
from airplanes.tests.factories import AirlinesFactory
from airports.tests.factories import AirportsFactory
from users.tests.factories import UserFactory
from django.urls import reverse


URL_AIRLINES = reverse('airlines-list')


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
def test_create_airlines_existing_title(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    existing_airline = AirlinesFactory()
    airlines_data = AirlinesFactory.build(title=existing_airline.title)
    payload = {
        "title": airlines_data.title,
        "detail": airlines_data.detail,
        "data_of_create": airlines_data.data_of_create,
        "slogan": airlines_data.slogan,
        "airport": existing_airline.airport.title,
    }
    response = api_client.post(URL_AIRLINES, data=payload)
    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_create_airlines_invalid_airport(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    airlines_data = AirlinesFactory.build()
    payload = {
        "title": airlines_data.title,
        "detail": airlines_data.detail,
        "data_of_create": airlines_data.data_of_create,
        "slogan": airlines_data.slogan,
        "airport": "NonExistentAirport",
    }
    response = api_client.post(URL_AIRLINES, data=payload)
    assert response.status_code == 400



@pytest.mark.django_db
def test_get_airlines_list(api_client):
    AirlinesFactory.create_batch(3)
    response = api_client.get(URL_AIRLINES)
    assert response.status_code == 200
    assert (len(response.data)) == 3


@pytest.mark.django_db
def test_get_airlines_retrieve(api_client):
    airline = AirlinesFactory()
    response = api_client.get(f"{URL_AIRLINES}{airline.id}/")
    assert response.status_code == 200
    assert response.data["id"] == airline.id
    assert response.data["title"] == airline.title
    assert response.data["detail"] == airline.detail
    assert response.data["data_of_create"] == str(airline.data_of_create)
    assert response.data["slogan"] == airline.slogan
    assert response.data["airport"] == airline.airport.title


@pytest.mark.django_db
def test_update_airlines(api_client):
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(user=admin)

    airline = AirlinesFactory()
    new_airport = AirportsFactory()
    payload = {
        "title": "UpdatedAirline",
        "detail": "UpdatedDetail",
        "data_of_create": "2023-01-01",
        "slogan": "UpdatedSlogan",
        "airport": new_airport.title,
    }
    response = api_client.put(f"{URL_AIRLINES}{airline.id}/", data=payload)
    assert response.status_code == 200
    assert response.data["title"] == "UpdatedAirline"
    assert response.data["detail"] == "UpdatedDetail"
    assert response.data["data_of_create"] == "2023-01-01"
    assert response.data["slogan"] == "UpdatedSlogan"
    assert response.data["airport"] == new_airport.title
