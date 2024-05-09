from rest_framework import serializers
from .models import TextProcessing

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
