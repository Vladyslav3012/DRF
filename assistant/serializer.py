from rest_framework import serializers
from .models import GeminiChatSession, GeminiChatMessage


class GeminiChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeminiChatMessage
        fields = ["role", "content", "created_at"]


class GeminiSessionSerializer(serializers.ModelSerializer):
    messages = GeminiChatMessageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = GeminiChatSession
        fields = ['chat_id', 'title',
                  'model_name', 'created_at', 'messages']


class GeminiMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeminiChatMessage
        fields = ['id', 'role', 'content',
                  'created_at']


class GeminiMessageInput(serializers.Serializer):
    prompt = serializers.CharField(min_length=1, required=True)
