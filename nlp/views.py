from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TextProcessing, LdaTopicModelling
from .serializers import TextProcessingSerializer, LdaTopicModellingSerializer
from .srs_text_processor import process_pdf
from users.models import UserUpload
from .lda_srs_modelling import train_lda_models, save_selected_lda_model

def truncate_path(full_path):
    """
    Truncates a full path to start from 'media/uploads/'.
    Args:
        full_path: The full path to truncate.
    Returns:
        The truncated path starting from 'media/uploads/'.
    Todo:
        Implement a better filter to hadle relative paths
    """
    return full_path.split("/home/steve/NRF/", 1)[1] if "NRF/" in full_path else full_path

def clean_filename(filename):
    """
        Cleans and extracts the filename (without extension) up to five words.
        Args:
            filename: The filename to clean.
        Returns:
            The cleaned filename limited to five words (without extension).
    """
    # Split filename by underscores or spaces (assuming word separators)
    words = filename.split("_") if "_" in filename else filename.split()
    # Truncate to maximum 5 words and join back with underscores
    cleaned_filename = "_".join(words[:10])
    # Remove extension (if present)
    cleaned_filename = cleaned_filename.split(".")[0]
    return cleaned_filename.split("uploads/", 1)[1] if "uploads/" in cleaned_filename else cleaned_filename
def transform_data_format(data):
    transformed_data = []

    num_topics = data['num_topics']
    coherence_values = data['coherence_values']

    # Iterate through num_topics and coherence_values and create dictionaries
    for topic, coherence in zip(num_topics, coherence_values):
        transformed_data.append({
            "no_of_topics": topic,
            "coherence_value": coherence
        })

    return transformed_data

class TextProcess(APIView):
    def post(self, request, format=None):
        user_upload_id = request.data.get('user_upload_id')
        start_page = int(request.data.get('start_page', 1))
        end_page = int(request.data.get('end_page', 1))
        
        try:
            user_upload = UserUpload.objects.get(pk=user_upload_id)
        except UserUpload.DoesNotExist:
            return Response({'error': 'File upload was not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Process the PDF file using srs_text_processor
        try:
            (corpus_path, dictionary_path, processed_text_path) = process_pdf(truncate_path(user_upload.document.path), start_page, end_page, clean_filename(user_upload.document.name))
        except Exception as e:
            return Response({'error': f'Error processing PDF: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create a new TextProcessing instance
        text_processing = TextProcessing.objects.create(
            user=request.user,
            user_upload=user_upload,
            start_page=start_page,
            end_page=end_page,
            processed_text_path=processed_text_path,  
            corpus_path=corpus_path,          
            dictionary_path=dictionary_path       
        )

        # Serialize the TextProcessing instance
        serializer = TextProcessingSerializer(text_processing)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProcessedDocsListView(generics.ListAPIView):
    queryset = TextProcessing.objects.all()
    serializer_class = TextProcessingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TextProcessing.objects.filter(user=self.request.user)

class LdaTopics(APIView):    
    def post(self, request, format=None):
        text_processing_id = request.data.get('text_processing_id')
        try:
            text_processing = TextProcessing.objects.get(pk=text_processing_id)
        except TextProcessing.DoesNotExist:
            return Response({'error': 'Preprocessed text was not found for this entry'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            (plotPayload) = train_lda_models(text_processing)
        except Exception as e:
            return Response({'error': f'Error training model: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create a new LdaTopicModel instance
        lda_model_instance = LdaTopicModelling.objects.create(
            user=request.user,
            user_upload=UserUpload.objects.get(pk=text_processing.user_upload_id),
            text_processing=text_processing
        )
        return Response({'lda_model_instance': lda_model_instance.id,'topic_coherence_results': transform_data_format(plotPayload)}, status=status.HTTP_200_OK)

class LdaTopicsSave(APIView):
    def patch(self, request, pk, format=None):
        try:
            lda_topic_model_instance = LdaTopicModelling.objects.get(pk=pk)
        except LdaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        selected_topics = request.data.get('selected_topics')
        lda_topic_model_instance.selected_topics = selected_topics
        lda_topic_model_instance.save()
        try:
            user_upload = UserUpload.objects.get(pk=lda_topic_model_instance.user_upload_id)
            (lda_path, coherence) = save_selected_lda_model(lda_topic_model_instance, clean_filename(user_upload.document.name))
            lda_topic_model_instance.lda_topics_file_path = lda_path
            lda_topic_model_instance.coherence_value = coherence
            lda_topic_model_instance.save()
        except Exception as e:
            return Response({'error': f'Error updating and saving lda coherent model: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'topics': lda_topic_model_instance.selected_topics, 'name': clean_filename(user_upload.document.name), 'dir': lda_path, 'coherence': coherence})
    
class LdaTopicModellingListView(generics.ListAPIView):
    queryset = LdaTopicModelling.objects.all()
    serializer_class = LdaTopicModellingSerializer

    def get_queryset(self):
        return LdaTopicModelling.objects.filter(user=self.request.user)
