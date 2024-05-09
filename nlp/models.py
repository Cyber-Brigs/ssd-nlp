import uuid
from django.db import models
from django.conf import settings
from users.models import UserUpload

class TextProcessing(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_upload = models.ForeignKey(UserUpload, on_delete=models.CASCADE)
    start_page = models.PositiveIntegerField()
    end_page = models.PositiveIntegerField()
    processed_text_path = models.FileField(upload_to='processed_files/texts/')
    corpus_path = models.FileField(upload_to='processed_files/corpora/')
    dictionary_path = models.FileField(upload_to='processed_files/dictionaries/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'TextProcessing ID: {self.id}'
