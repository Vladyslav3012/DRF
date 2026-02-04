import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
def test_create_user(user):
    assert user.username.startswith("user")
    assert user.pk is not None
    assert not user.is_active
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser():
    superuser = User.objects.create_superuser(
        username="adminuser",
        email="test_admin@gmail.com",
        password = "adminpassword123",
    )
    assert superuser.username == "adminuser"
    assert superuser.email == "test_admin@gmail.com"
    assert superuser.check_password("adminpassword123")
    assert superuser.pk is not None
    assert superuser.is_staff
    assert superuser.is_superuser
    assert superuser.is_active

