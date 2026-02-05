from datetime import timedelta

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@gmail.com")
    otp = factory.Sequence(lambda n: f"{n:06d}")
    otp_expire = timezone.now() + timedelta(minutes=5)
    otp_try = 3
    password = factory.PostGenerationMethodCall('set_password',
                                                'testpassword123')
