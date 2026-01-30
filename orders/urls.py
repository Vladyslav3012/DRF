from django.urls import path
from Project.settings import DEBUG
from .views import OrderListCreateApiView, OrderUpdateApiView, StripeApiView, StripeWebhookAPIView, WebhookExpireApiView


urlpatterns = [
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