from rest_framework import serializers
from .models import TextProcessing, LdaTopicModelling, LsaTopicModelling

class TextProcessingSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    user_upload_id = serializers.ReadOnlyField(source='user_upload.id')
    start_page = serializers.IntegerField()
    end_page = serializers.IntegerField()
    processed_text_file = serializers.SerializerMethodField()
    corpus_file = serializers.SerializerMethodField()
    dictionary_file = serializers.SerializerMethodField()
    time_created = serializers.DateTimeField(source='created_at')
    document_name = serializers.SerializerMethodField()
    # status = serializers.CharField()
    def get_document_name(self, instance):
        return instance.user_upload.document_name
    def get_processed_text_file(self, instance):
        return bool(instance.processed_text_path.name and instance.processed_text_path)

    def get_corpus_file(self, instance):
        return bool(instance.corpus_path.name and instance.corpus_path)

    def get_dictionary_file(self, instance):
        return bool(instance.dictionary_path.name and instance.dictionary_path)

    class Meta:
        model = TextProcessing
        fields = ('id', 'user_id', 'user_upload_id', 'document_name', 'start_page', 'end_page', 'processed_text_file', 'corpus_file','status', 'dictionary_file', 'time_created')

class LdaTopicModellingSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    user_upload_id = serializers.ReadOnlyField(source='user_upload.id')
    text_processing_id = serializers.ReadOnlyField(source='text_processing.id')
    lda_topics_file_path = serializers.SerializerMethodField()
    time_created = serializers.DateTimeField(source='created_at')

    def get_lda_topics_file_path(self, instance):
        return instance.lda_topics_file_path.name if instance.lda_topics_file_path else None

    class Meta:
        model = LdaTopicModelling
        fields = ('id', 'user_id', 'user_upload_id', 'text_processing_id', 'lda_topics_file_path', 'selected_topics', 'coherence_value', 'time_created')

class LsaTopicModellingSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    user_upload_id = serializers.ReadOnlyField(source='user_upload.id')
    text_processing_id = serializers.ReadOnlyField(source='text_processing.id')
    lsa_topics_file_path = serializers.SerializerMethodField()
    time_created = serializers.DateTimeField(source='created_at')

    def get_lsa_topics_file_path(self, instance):
        return instance.lsa_topics_file_path.name if instance.lsa_topics_file_path else None

    class Meta:
        model = LsaTopicModelling
        fields = ('id', 'user_id', 'user_upload_id', 'text_processing_id', 'lsa_topics_file_path', 'selected_topics', 'coherence_value', 'time_created')
