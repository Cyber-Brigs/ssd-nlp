import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    # Add custom fields if needed
    pass

User = get_user_model()

class UserUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    document = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(max_length=255)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    def __str__(self):
        return self.document_name