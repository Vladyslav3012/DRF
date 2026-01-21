from django.urls import  path
from .views import GeminiSessionView, GeminiChatDetailView

urlpatterns = [
    path('chats/', GeminiSessionView.as_view(), name='chat-list'),
    path('chats/<uuid:chat_id>/', GeminiChatDetailView.as_view(), name='chat-detail'),
]