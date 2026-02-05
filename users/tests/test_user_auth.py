import pytest
from django.urls import reverse
from users.models import CustomUser
from users.tests.factories import UserFactory

url_to_sign = reverse('signup')
url_to_login = reverse('login')

"""
TESTING USER SIGNUP
"""
@pytest.mark.django_db
def test_signup_user(api_client):
    user_data = UserFactory.build()
    payload = {
        "email": user_data.email,
        "username": user_data.username,
        "password": "testpassword123",
    }
    response = api_client.post(url_to_sign, data=payload)

    assert response.status_code == 201
    data = response.data['data']
    assert data['username'] == user_data.username
    assert data['email'] == user_data.email
    assert 'password' not in data

    assert CustomUser.objects.filter(email=user_data.email).exists()
    new_user = CustomUser.objects.get(email=user_data.email)
    assert new_user.is_active == False
    assert new_user.check_password("testpassword123")

@pytest.mark.django_db
def test_signup_user_existing_email(api_client):
    existing_user = UserFactory()
    payload = {
        "email": existing_user.email,
        "username": "newuser",
        "password": "testpassword123",
    }
    response = api_client.post(url_to_sign, data=payload)
    assert response.status_code == 400
    assert CustomUser.objects.filter(email=existing_user.email).count() == 1


"""
TESTING USER AUTHENTICATION
"""
@pytest.mark.django_db
def test_user_authentication(api_client):
    password = "testpassword123"
    user = UserFactory(password=password)
    user.is_active = True
    user.save()

    payload = {
        "email": user.email,
        "password": password,
    }
    response = api_client.post(url_to_login, data=payload)

    assert response.status_code == 200
    assert 'token' in response.data


@pytest.mark.django_db
def test_user_authentication_invalid_credentials(api_client):
    payload = {
        "email": "nonexistentuser@gmail.com",
        "password": "wrongpassword",
    }
    response = api_client.post(url_to_login, data=payload)
    assert response.status_code == 401
    assert 'token' not in response.data


"""
TESTING GET AUTHENTICATED USER DETAILS
"""
@pytest.mark.django_db
def test_get_auth_user(user, auth_user):
    response = auth_user.get(url_to_login)
    assert response.status_code == 200
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email
    assert 'password' not in response.data

@pytest.mark.django_db
def test_get_unauth_user(api_client):
    response = api_client.get(url_to_login)
    assert response.status_code == 401
    assert not response.data.get('username')
    assert not response.data.get('email')


"""
TESTING EMAIL VERIFICATION SIGNAL
"""
@pytest.mark.django_db
def test_email_verification_signal(mocker, api_client):
    user = UserFactory.build()
    payload = {
        "email": user.email,
        "username": user.username,
        "password": "testpassword123",
    }
    send_email_mock = mocker.patch(
        'users.signals.send_email_task.delay_on_commit'
    )
    response = api_client.post(url_to_sign, data=payload)

    assert response.status_code == 201
    send_email_mock.assert_called_once()
    assert send_email_mock.call_args[0][0] == "Your gmail has been register on our website"
    assert user.email in send_email_mock.call_args[0][2]