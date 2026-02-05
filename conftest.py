import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def admin():
    return UserFactory(is_staff=True)

@pytest.fixture
def auth_admin(api_client, admin):
    api_client.force_authenticate(user=admin)
    return api_client

@pytest.fixture
def auth_user(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client