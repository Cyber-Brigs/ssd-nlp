from django.urls import path
from .views import TextProcess, ProcessedDocsListView, LdaTopics, LdaTopicsSave, LdaTopicModellingListView

urlpatterns = [
    path('process-text/', TextProcess.as_view(), name='process-text'),
    path('processed-texts/', ProcessedDocsListView.as_view(), name='processed-texts'),
    path('lda-model-topics/', LdaTopics.as_view(), name='lda-topics'),
    path('lda-select-topics/<uuid:pk>/', LdaTopicsSave.as_view(), name='lda-selected-topics'),
    path('lda-models-view/', LdaTopicModellingListView.as_view(), name='lda-view-models')
]
