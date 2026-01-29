from django.urls import path
from Project.settings import DEBUG
from .views import (SignUpView, LogInView, OrderListCreateApiView,
                    OrderUpdateApiView, StripeApiView,
                    StripeWebhookAPIView, WebhookExpireApiView, ActivateUserApiView,
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

    path('orders/', OrderListCreateApiView.as_view()),
    path('orders/<str:pk>/', OrderUpdateApiView.as_view()),
    path('orders/<str:pk>/', OrderUpdateApiView.as_view()),
    path("check-session/<uuid:order_id>/", StripeApiView.as_view()),
    path("stripe-webhook/<str:token>/", StripeWebhookAPIView.as_view()),
]

if DEBUG:
    urlpatterns += [
        path('webhook-expired/<uuid:order_id>/', WebhookExpireApiView.as_view())
    ]
