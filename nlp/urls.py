from django.urls import path
from .views import TextProcess, ProcessedDocsListView, LdaTopics, LdaTopicsSave, LdaTopicModellingListView, LsaTopics, LsaTopicsSave, LsaTopicModellingListView, LdaCosineCapecResults, LsaCosineCapecResults

urlpatterns = [
    path('process-text/', TextProcess.as_view(), name='process-text'),
    path('processed-texts/', ProcessedDocsListView.as_view(), name='processed-texts'),
    path('lda-model-topics/', LdaTopics.as_view(), name='lda-topics'),
    path('lda-select-topics/<uuid:pk>/', LdaTopicsSave.as_view(), name='lda-selected-topics'),
    path('lda-models-view/', LdaTopicModellingListView.as_view(), name='lda-view-models'),
    path('lsa-model-topics/', LsaTopics.as_view(), name='lsa-topics'),
    path('lsa-select-topics/<uuid:pk>/', LsaTopicsSave.as_view(), name='lsa-selected-topics'),
    path('lsa-models-view/', LsaTopicModellingListView.as_view(), name='lsa-view-models'),
    path('lda-results/<uuid:pk>/<uuid:text_processing_id>/', LdaCosineCapecResults.as_view(), name='lda-results'),
    path('lsa-results/<uuid:pk>/<uuid:text_processing_id>/', LsaCosineCapecResults.as_view(), name='lsa-results')
]
