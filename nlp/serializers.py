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

    def get_processed_text_file(self, instance):
        return instance.processed_text_path.name if instance.processed_text_path else None

    def get_corpus_file(self, instance):
        return instance.corpus_path.name if instance.corpus_path else None

    def get_dictionary_file(self, instance):
        return instance.dictionary_path.name if instance.dictionary_path else None

    class Meta:
        model = TextProcessing
        fields = ('id', 'user_id', 'user_upload_id','start_page', 'end_page', 'processed_text_file', 'corpus_file', 'dictionary_file', 'time_created')

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
