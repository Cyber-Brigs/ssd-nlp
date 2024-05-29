# In users/urls.py
from django.urls import path
from .views import UserCreate, UserLogin, UserAccountView, UserUploadView, UserUploadListView, UserStatisticsView

urlpatterns = [
    path('register/', UserCreate.as_view(), name='user-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('user/', UserAccountView.as_view(), name='user-account'),
    path('upload/', UserUploadView.as_view(), name='user-upload'),
    path('uploads/', UserUploadListView.as_view(), name='user-uploads'),
    path('user/statistics/', UserStatisticsView.as_view(), name='user-statistics'),
]
