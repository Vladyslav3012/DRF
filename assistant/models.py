import uuid

from django.db import models

from users.models import CustomUser


class GeminiChatSession(models.Model):

    class ModelChoice(models.TextChoices):
        gemini_3_flash = "gemini-3-flash-preview"
        gemini_2_5_flash = "gemini-2.5-flash"
        gemini_2_5_flash_lite = "gemini-2.5-flash-lite"

    chat_id = models.UUIDField(primary_key=True,
                               default=uuid.uuid4,
                               editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="chat_session")
    title = models.CharField(max_length=255,
                             blank=True, null=True,
                             default="New chat")
    model_name = models.CharField(max_length=50,
                                  choices=ModelChoice.choices,
                                  default=ModelChoice.gemini_2_5_flash_lite)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} #{self.chat_id}"


class GeminiChatMessage(models.Model):

    class RoleChoice(models.TextChoices):
        USER = "user", 'User'
        MODEL = 'model', 'Model'

    session = models.ForeignKey(GeminiChatSession, on_delete=models.CASCADE,
                                related_name="messages")
    role = models.CharField(max_length=10, choices=RoleChoice.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
