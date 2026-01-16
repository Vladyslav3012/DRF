from django.urls import path
from .views import (SignUpView, LogInView, OrderListCreateApiView,
                    OrderUpdateApiView, StripeApiView,
                    StripeWebhookAPIView)

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LogInView.as_view()),
    path('orders/', OrderListCreateApiView.as_view()),
    path('orders/<str:pk>/', OrderUpdateApiView.as_view()),
    path("check-session/<uuid:order_id>/", StripeApiView.as_view()),
    path("stripe-webhook/", StripeWebhookAPIView.as_view()),
]
