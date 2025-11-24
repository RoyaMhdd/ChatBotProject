from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number or ""


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    attempts = models.IntegerField(default=0)

    def is_valid(self):
        return timezone.now() < self.expires_at and self.attempts < 5
    
    def can_request_new(self):
        return timezone.now() > self.created_at + timedelta(seconds=60)
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"
    
