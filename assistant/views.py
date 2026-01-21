from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from .serializer import (GeminiSessionSerializer, GeminiMessageSerializer,
                         GeminiMessageInput)

from .models import GeminiChatSession, GeminiChatMessage
from rest_framework.request import Request
from rest_framework.response import Response
from .service import ask_to_gemini, create_title


class GeminiSessionView(generics.ListCreateAPIView):
    serializer_class = GeminiSessionSerializer

    def get_queryset(self):
        return GeminiChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GeminiChatDetailView(APIView):

    def get_session(self, chat_id, user):
        return get_object_or_404(GeminiChatSession, chat_id=chat_id, user=user)

    def get(self, request, chat_id):
        session = self.get_session(chat_id, request.user)
        messages = GeminiChatMessage.objects.filter(session=session).order_by('created_at')
        serializer = GeminiSessionSerializer(messages, many=True)

        return Response({
            "session": GeminiSessionSerializer(session).data,
            "messages": serializer.data
        })

    @extend_schema(request=GeminiMessageInput)
    def post(self, request, chat_id):
        session = self.get_session(chat_id, request.user)

        input_serializer = GeminiMessageInput(data=request.data)
        if input_serializer.is_valid():
            user_prompt = input_serializer.validated_data['prompt']

            GeminiChatMessage.objects.create(
                session=session,
                role=GeminiChatMessage.RoleChoice.USER,
                content=user_prompt
            )

            history_messages = GeminiChatMessage.objects.filter(session=session).order_by('created_at')

            ai_response = ask_to_gemini(
                model=session.model_name,
                history=history_messages,
                user_prompt=user_prompt
            )

            GeminiChatMessage.objects.create(
                session=session,
                role=GeminiChatMessage.RoleChoice.MODEL,
                content=ai_response
            )

            if GeminiChatMessage.objects.filter(session=session).count() <= 2:
                new_title = create_title(session.model_name, user_prompt)
                session.title = new_title
                session.save()

            return Response({
                "role": "model",
                "content": ai_response,
                "chat_title": session.title
            }, status=200)

        return Response(input_serializer.errors, status=400)