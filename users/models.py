from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    ROLE_CHOICES = [
        ('normal', 'Normal User'),
        ('admin', 'Company Admin'),
    ]

    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)

    fullName = models.CharField(max_length=50, blank=True)

    email = models.EmailField(null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)

    #to check if user completed profile and login for first time
    is_profile_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=64, null=True, blank=True)

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
    


    
