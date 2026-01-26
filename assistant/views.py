from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from .serializer import (GeminiSessionSerializer, GeminiMessageSerializer,
                         GeminiMessageInput)

from .models import GeminiChatSession, GeminiChatMessage
from rest_framework.response import Response
from .service import ask_to_gemini, create_title


@extend_schema(tags=['Assistant'])
class GeminiSessionView(generics.ListCreateAPIView):
    serializer_class = GeminiSessionSerializer

    def get_queryset(self):
        return GeminiChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Assistant'])
class GeminiChatDetailView(APIView):

    def get_session(self, chat_id, user):
        return get_object_or_404(GeminiChatSession, chat_id=chat_id, user=user)

    def get(self, request, chat_id):
        session = self.get_session(chat_id, request.user)
        serializer = GeminiSessionSerializer(session)

        return Response(serializer.data)

    def delete(self, request, chat_id):
        chat = self.get_session(chat_id, request.user)
        chat.delete()
        return Response(status=204)
