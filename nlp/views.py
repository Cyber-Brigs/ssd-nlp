from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import TextProcessing, LdaTopicModelling, LsaTopicModelling
from .serializers import TextProcessingSerializer, LdaTopicModellingSerializer, LsaTopicModellingSerializer
from .srs_text_processor import process_pdf
from users.models import UserUpload
from .lda_srs_modelling import train_lda_models, save_selected_lda_model
from .lsa_srs_modelling import train_lsa_models, save_selected_lsa_model
from .lda_cosine import generate_lda_capec_results
from .lsa_cosine import generate_lsa_capec_results
import csv

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

def read_csv_file(file_path):
    """Reads a CSV file and returns a dictionary with ID as the key and the rest of the data as values."""
    capec_dict = {}
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            capec_id = int(row['ID'])
            capec_dict[capec_id] = row
    return capec_dict

def serialize_vulnerabilities(vulnerability_list, csv_data):
    """Transforms a list of vulnerabilities using the CSV data into detailed objects."""
    detailed_vulnerabilities = []
    for item in vulnerability_list:
        capec_id = item['capec_id']
        coherence = item['coherence']
        if capec_id in csv_data:
            detailed_vulnerability = csv_data[capec_id]
            detailed_vulnerability['coherence'] = coherence  # Add coherence value to the detailed data
            detailed_vulnerabilities.append(detailed_vulnerability)
    return detailed_vulnerabilities

# Path to the CSV file
csv_file_path = 'nlp/CAPEC/Comprehensive CAPEC Dictionary.csv'
# Read the CSV file
csv_data = read_csv_file(csv_file_path)

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
            with default_storage.open(user_upload.document.name, 'rb') as file_obj:
                (corpus_path, dictionary_path, processed_text_path) = process_pdf(file_obj, start_page, end_page, clean_filename(user_upload.document.name))
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

class LsaTopics(APIView):    
    def post(self, request, format=None):
        text_processing_id = request.data.get('text_processing_id')
        try:
            text_processing = TextProcessing.objects.get(pk=text_processing_id)
        except TextProcessing.DoesNotExist:
            return Response({'error': 'Preprocessed text was not found for this entry'}, status=status.HTTP_404_NOT_FOUND)
        
        try:            
            (plotPayload) = train_lsa_models(text_processing)
        except Exception as e:
            return Response({'error': f'Error training model: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create a new LdaTopicModel instance
        lsa_model_instance = LsaTopicModelling.objects.create(
            user=request.user,
            user_upload=UserUpload.objects.get(pk=text_processing.user_upload_id),
            text_processing=text_processing
        )
        return Response({'lda_model_instance': lsa_model_instance.id,'topic_coherence_results': transform_data_format(plotPayload)}, status=status.HTTP_200_OK)

class LsaTopicsSave(APIView):
    def patch(self, request, pk, format=None):
        try:
            lsa_topic_model_instance = LsaTopicModelling.objects.get(pk=pk)
        except LsaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        selected_topics = request.data.get('selected_topics')
        lsa_topic_model_instance.selected_topics = selected_topics
        lsa_topic_model_instance.save()
        try:
            user_upload = UserUpload.objects.get(pk=lsa_topic_model_instance.user_upload_id)
            (lsa_path, coherence) = save_selected_lsa_model(lsa_topic_model_instance, clean_filename(user_upload.document.name))
            lsa_topic_model_instance.lsa_topics_file_path = lsa_path
            lsa_topic_model_instance.coherence_value = coherence
            lsa_topic_model_instance.save()
        except Exception as e:
            return Response({'error': f'Error updating and saving lda coherent model: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'topics': lsa_topic_model_instance.selected_topics, 'name': clean_filename(user_upload.document.name), 'dir': lsa_path, 'coherence': coherence})
    
class LsaTopicModellingListView(generics.ListAPIView):
    queryset = LsaTopicModelling.objects.all()
    serializer_class = LsaTopicModellingSerializer

    def get_queryset(self):
        return LsaTopicModelling.objects.filter(user=self.request.user)
    
class LdaCosineCapecResults(APIView):
    def get(self, request, format=None):
        pk = request.query_params.get('pk', None)
        text_processing_id = request.query_params.get('text_processing_id', None)
        if not pk or not text_processing_id:
            return Response({'error': 'lda_model_id and text_processing_id query parameters are required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            lda_topic_model_instance = LdaTopicModelling.objects.get(pk=pk)
        except LdaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            text_processing_instance = get_object_or_404(TextProcessing, pk=text_processing_id) 
            user_upload = UserUpload.objects.get(pk=lda_topic_model_instance.user_upload_id)
            file_name  = clean_filename(user_upload.document.name) 
            lda_file_url = lda_topic_model_instance.lda_topics_file_path
            (lda_top_results) = generate_lda_capec_results(file_name, lda_file_url)
        except Exception as e:
            return Response({'error': f'Error obtaining processing files: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        lda_topic_model_instance.results = lda_top_results
        lda_topic_model_instance.save()
        detailed_vulnerabilities = serialize_vulnerabilities(lda_top_results, csv_data)
        return Response({'message': 'success','results': detailed_vulnerabilities})

class LsaCosineCapecResults(APIView):
    def get(self, request, format=None):
        pk = request.query_params.get('pk', None)
        text_processing_id = request.query_params.get('text_processing_id', None)
        if not pk or not text_processing_id:
            return Response({'error': 'lsa_model_id and text_processing_id query parameters are required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            lsa_topic_model_instance = LsaTopicModelling.objects.get(pk=pk)
        except LsaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            text_processing_instance = get_object_or_404(TextProcessing, pk=text_processing_id) 
            user_upload = UserUpload.objects.get(pk=lsa_topic_model_instance.user_upload_id)
            file_name  = clean_filename(user_upload.document.name) 
            lsa_file_url= lsa_topic_model_instance.lsa_topics_file_path
            (lsa_top_results) = generate_lsa_capec_results(text_processing_instance, file_name, lsa_file_url)
        except Exception as e:
            return Response({'error': f'Error obtaining processing files: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        lsa_topic_model_instance.results = lsa_top_results
        lsa_topic_model_instance.save()
        detailed_vulnerabilities = serialize_vulnerabilities(lsa_top_results, csv_data)
        return Response({'message': 'success','results': detailed_vulnerabilities})
    
class LdaViewResults(APIView):
    def get(self, request, format=None):
        pk = request.query_params.get('id', None)
        if not pk:
            return Response({'error': 'lsa model identifier parameter is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            lda_topic_model_instance = LdaTopicModelling.objects.get(pk=pk)
        except LsaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        results_object = lda_topic_model_instance.results
        detailed_vulnerabilities = serialize_vulnerabilities(results_object, csv_data)
        return Response({'message': 'success','results': detailed_vulnerabilities})

class LsaViewResults(APIView):
    def get(self, request, format=None):
        pk = request.query_params.get('id', None)
        if not pk:
            return Response({'error': 'lsa model identifier parameter is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            lsa_topic_model_instance = LsaTopicModelling.objects.get(pk=pk)
        except LsaTopicModelling.DoesNotExist:
            return Response({'error': 'Topic Model instance was not found'}, status=status.HTTP_404_NOT_FOUND)
        results_object = lsa_topic_model_instance.results
        detailed_vulnerabilities = serialize_vulnerabilities(results_object, csv_data)
        return Response({'message': 'success','results': detailed_vulnerabilities})
