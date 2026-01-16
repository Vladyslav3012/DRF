from django.urls import path
from .views import (SignUpView, LogInView, OrderListCreateApiView,
                    OrderUpdateApiView, GeminiAPIView)

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LogInView.as_view()),
    path('orders/', OrderListCreateApiView.as_view()),
    path('orders/<str:pk>/', OrderUpdateApiView.as_view()),
    path('assistant', GeminiAPIView.as_view())
]
