from django.urls import path
from .views import (SignUpView, LogInView, ActivateUserApiView,
                    RefreshOTPApiView, ChangePasswordApiView,
                    ChangePasswordRequestOTP, SetNewPasswordWithOTP, test_email_view)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),

    path('activate/', ActivateUserApiView.as_view(), name='activate'),
    path('activate/refresh', RefreshOTPApiView.as_view(), name='refresh-otp'),
path('test-email/', test_email_view),

    path('change-password/', ChangePasswordApiView.as_view()),
    path('change-password/request-otp', ChangePasswordRequestOTP.as_view()),
    path('change-password/with-otp', SetNewPasswordWithOTP.as_view()),
]
