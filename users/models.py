import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(unique=True, blank=False)
    # Add custom fields if needed
    def __str__(self):
        return self.email

User = get_user_model()

class UserUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    document = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(max_length=255, unique=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')
    def __str__(self):
        return self.document_name