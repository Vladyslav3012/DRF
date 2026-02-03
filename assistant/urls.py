from django.urls import path
from .views import GeminiSessionView, GeminiChatDetailView, chat_page

urlpatterns = [
    path('chats/', GeminiSessionView.as_view(), name='chat-list'),
    path('chats/<uuid:chat_id>/', GeminiChatDetailView.as_view(), name='chat-detail'),
    path("chat/", chat_page, name="assistant_chat_root"),
    path("chat/<uuid:chat_id>/", chat_page, name="assistant_chat"),
]
