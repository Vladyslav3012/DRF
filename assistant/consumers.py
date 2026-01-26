import json
import logging

import google.genai.errors
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import GeminiChatSession, GeminiChatMessage
from .service import ask_to_gemini, create_title

logger = logging.getLogger(__name__)


class GeminiSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope['user']
        is_allowed = await self.get_chat(pk=self.chat_id, user=self.user)
        if not is_allowed:
            await self.close(code=404)
            return
        await self.accept()

    async def disconnect(self, code):
        await super().disconnect(code=code)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            user_prompt = data.get('prompt')

            if not user_prompt:
                return

            await self.send(text_data=json.dumps({
                'role': 'user',
                'content': user_prompt
            }))

            user_message = await self.save_message(role='user', content=user_prompt)

            response = await self.get_gemini_response(user_prompt=user_prompt,
                                                      exclude_msg=user_message.id)
            await self.save_message(role='model', content=response)

            await self.create_title(user_prompt)

            await self.send(text_data=json.dumps({
                'role': 'model',
                'content': response
            }))
        except Exception as e:
            logger.exception(f"Error : {e}")
            await self.send(text_data=json.dumps({"Error": "Sorry, something went wrong"}))

    @database_sync_to_async
    def save_message(self, role, content):
        session = GeminiChatSession.objects.get(chat_id=self.chat_id)
        return GeminiChatMessage.objects.create(
            session=session,
            role=role,
            content=content
        )

    @database_sync_to_async
    def create_title(self, user_prompt):
        session = GeminiChatSession.objects.get(chat_id=self.chat_id)
        if session.title == "New chat" or not session.title:
            new_title = create_title(model=session.model_name, user_prompt=user_prompt)
            session.title = new_title
            session.save()


    @database_sync_to_async
    def get_chat(self, pk, user):
        try:
            return GeminiChatSession.objects.filter(chat_id=pk, user=user).exists()
        except Exception:
            return False


    @database_sync_to_async
    def get_gemini_response(self, user_prompt, exclude_msg=None):
        session = GeminiChatSession.objects.get(chat_id=self.chat_id)
        history = GeminiChatMessage.objects.filter(session=session).order_by('created_at')
        if exclude_msg:
            history.exclude(id=exclude_msg)
        response = ask_to_gemini(
            model=session.model_name,
            user_prompt=user_prompt,
            history=history,
            user_id=self.user.id
        )
        return response





