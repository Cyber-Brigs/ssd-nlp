from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TextProcessing
from .serializers import TextProcessingSerializer
from .srs_text_processor import process_pdf
from users.models import UserUpload

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

class TextProcess(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    

    def post(self, request, format=None):
        user_upload_id = request.data.get('user_upload_id')
        start_page = int(request.data.get('start_page', 1))
        end_page = int(request.data.get('end_page', 1))
        # user_upload = UserUpload.objects.get(pk=user_upload_id)
        
        try:
            user_upload = UserUpload.objects.get(pk=user_upload_id)
        except UserUpload.DoesNotExist:
            return Response({'error': 'File upload was not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Process the PDF file using srs_text_processor
        try:
            (corpus_path, dictionary_path, processed_text_path) = process_pdf(truncate_path(user_upload.document.path), start_page, end_page, clean_filename(user_upload.document.name))
        except Exception as e:
            print(truncate_path(user_upload.document.path), start_page, end_page, clean_filename(user_upload.document.name))
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
