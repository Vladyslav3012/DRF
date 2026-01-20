from django.urls import path
from Project.settings import DEBUG
from .views import (SignUpView, LogInView, OrderListCreateApiView,
                    OrderUpdateApiView, StripeApiView,
                    StripeWebhookAPIView, WebhookExpireApiView)

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LogInView.as_view()),
    path('orders/', OrderListCreateApiView.as_view()),
    path('orders/<str:pk>/', OrderUpdateApiView.as_view()),
    path("check-session/<uuid:order_id>/", StripeApiView.as_view()),
    path("stripe-webhook/<str:token>/", StripeWebhookAPIView.as_view()),
]

if DEBUG:
    urlpatterns += [
        path('webhook-expired/<uuid:order_id>/', WebhookExpireApiView.as_view())
    ]
