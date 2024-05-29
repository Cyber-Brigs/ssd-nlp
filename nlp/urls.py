from django.urls import path
from .views import TextProcess, ProcessedDocsListView, LdaTopics, LdaTopicsSave, LdaTopicModellingListView, LsaTopics, LsaTopicsSave, LsaTopicModellingListView, LdaCosineCapecResults, LsaCosineCapecResults, LdaViewResults, LsaViewResults

urlpatterns = [
    path('process-text/', TextProcess.as_view(), name='process-text'),
    path('processed-texts/', ProcessedDocsListView.as_view(), name='processed-texts'),
    path('lda-model-topics/', LdaTopics.as_view(), name='lda-topics'),
    path('lda-select-topics/<uuid:pk>/', LdaTopicsSave.as_view(), name='lda-selected-topics'),
    path('lda-models-view/', LdaTopicModellingListView.as_view(), name='lda-view-models'),
    path('lsa-model-topics/', LsaTopics.as_view(), name='lsa-topics'),
    path('lsa-select-topics/<uuid:pk>/', LsaTopicsSave.as_view(), name='lsa-selected-topics'),
    path('lsa-models-view/', LsaTopicModellingListView.as_view(), name='lsa-view-models'),
    path('lda-results/', LdaCosineCapecResults.as_view(), name='lda-results'),
    path('lsa-results/', LsaCosineCapecResults.as_view(), name='lsa-results'),
    path('view-lda-results/', LdaViewResults.as_view(), name='view-lda-results'),
    path('view-lsa-results/', LsaViewResults.as_view(), name='view-lsa-results')
]
