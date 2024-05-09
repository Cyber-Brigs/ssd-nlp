from django.urls import path
from .views import TextProcess, ProcessedDocsListView

urlpatterns = [
    path('process-text/', TextProcess.as_view(), name='process-text'),
    path('processed-texts/', ProcessedDocsListView.as_view(), name='processed-texts')
]
