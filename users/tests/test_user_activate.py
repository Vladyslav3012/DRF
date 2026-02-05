import pytest
from django.urls import reverse
from users.tests.factories import UserFactory


url_activate = reverse('activate')
url_refresh = reverse('refresh-otp')


@pytest.mark.django_db
def test_user_activation(api_client):
    user = UserFactory(is_active=False)
    otp = user.otp

    payload = {
        "email": user.email,
        "otp": otp,
    }
    response = api_client.post(url_activate, data=payload)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active == True
    assert user.otp is None
    assert user.otp_try is None
    assert user.otp_expire is None


@pytest.mark.django_db
def test_user_activation_invalid_otp(api_client):
    user = UserFactory(is_active=False)

    payload = {
        "email": user.email,
        "otp": 111111,
    }
    response = api_client.post(url_activate, data=payload)
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.is_active == False
    assert user.otp_try == 2
    assert user.otp_expire is not None


@pytest.mark.django_db
def test_user_activation_already_active(api_client):
    user = UserFactory(is_active=True)

    payload = {
        "email": user.email,
        "otp": user.otp,
    }
    response = api_client.post(url_activate, data=payload)
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.is_active == True


@pytest.mark.django_db
def test_refresh_otp(api_client):
    password = "testpassword123"
    user = UserFactory(is_active=False)
    user.set_password(password)
    user.save()

    payload = {
        "email": user.email,
        "password": password,
    }
    response = api_client.post(url_refresh, data=payload)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.otp is not None
    assert user.otp_try == 3
    assert user.otp_expire is not None


@pytest.mark.django_db
def test_refresh_otp_active_user(api_client):
    user = UserFactory(is_active=True)

    payload = {
        "email": user.email,
        "password": "testpassword123",
    }
    response = api_client.post(url_refresh, data=payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_refresh_otp_invalid_credentials(api_client):
    user = UserFactory(is_active=False)

    payload = {
        "email": user.email,
        "password": "wrongpassword",
    }
    response = api_client.post(url_refresh, data=payload)
    assert response.status_code == 400
