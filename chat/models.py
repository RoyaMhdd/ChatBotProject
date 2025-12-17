from django.db import models
from django.utils import timezone
from users.models import User 

class Conversation(models.Model):

    INVENTION_TYPE_CHOICES = [
        ("process", "Process"),
        ("product", "Product"),
        ("hybrid", "Hybrid"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True
    )

    invention_type = models.CharField(max_length=10, choices=INVENTION_TYPE_CHOICES, default="process")

    title = models.CharField(max_length=255, blank=True)

    last_form = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    details = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Conversation {self.id}"
    
class Message(models.Model):

    ROLE_USER = "user"
    ROLE_AI = "assistant"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_AI, "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    file = models.FileField(upload_to="chat_files/", null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."

class Invention(models.Model):
    
    INVENTION_TYPE_CHOICES = [
        ("process", "Process"),
        ("product", "Product"),
        ("hybrid", "Hybrid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventions")

    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="invention"
    )

    invention_type = models.CharField(max_length=10, choices=INVENTION_TYPE_CHOICES)
    
    final_text = models.TextField(null=True, blank=True)  # final output form
    file = models.FileField(upload_to="inventions/", null=True, blank=True)  # PDF or Word

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FormHistory(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="form_history"
    )

    version = models.IntegerField() 

    content = models.TextField()  

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Form v{self.version} for Conversation {self.conversation.id}"


