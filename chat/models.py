from django.db import models
from django.utils import timezone
from users.models import User 


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else f"Conversation {self.id}"


class Message(models.Model):
    
    ROLE_USER = "user"
    ROLE_AI = "assistant"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_AI, "Assistant"),
    ]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES) 
    content = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."





