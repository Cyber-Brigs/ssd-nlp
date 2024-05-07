# In users/urls.py
from django.urls import path
from .views import UserCreate, UserLogin, UserUploadView, UserUploadListView

urlpatterns = [
    path('register/', UserCreate.as_view(), name='user-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('upload/', UserUploadView.as_view(), name='user-upload'),
    path('uploads/', UserUploadListView.as_view(), name='user-uploads'),
]
