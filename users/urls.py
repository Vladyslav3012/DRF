from django.urls import path
from .views import (SignUpView, LogInView, ActivateUserApiView,
                    RefreshOTPApiView, ChangePasswordApiView,
                    ChangePasswordRequestOTP, SetNewPasswordWithOTP)

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LogInView.as_view()),

    path('activate/', ActivateUserApiView.as_view()),
    path('activate/refresh', RefreshOTPApiView.as_view()),

    path('change-password/', ChangePasswordApiView.as_view()),
    path('change-password/request-otp', ChangePasswordRequestOTP.as_view()),
    path('change-password/with-otp', SetNewPasswordWithOTP.as_view()),
]
