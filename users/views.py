from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, UserUploadSerializer
from .models import UserUpload
from nlp.models import TextProcessing, LdaTopicModelling, LsaTopicModelling
from .serializers import UserStatisticsSerializer

CustomUser = get_user_model()

class UserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserLogin(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username or not password:
            return Response({'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserAccountView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        user_id = request.query_params.get('ref', None)
        
        if not user_id:
            return Response({'error': 'User Identifier not supplied'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Extract user_id from the token
        token_user_id = request.user.id
        
        if str(token_user_id) != user_id:
            return Response({'error': 'Access denied. User ID mismatch.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'No user with identifier'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
     
class UserUploadView(generics.CreateAPIView):
    queryset = UserUpload.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        # Extract the document name from the uploaded file metadata
        document = self.request.FILES.get('document')
        document_name = document.name if document else ''
        
        # Check for uniqueness of the document
        if UserUpload.objects.filter(document_name=document_name).exists():
            raise ValidationError({"detail": "Please modify document name to avoid duplicity and security."})
        
        # Save the user and the document name automatically
        serializer.save(user=self.request.user, document_name=document_name)
        
class UserUploadListView(generics.ListAPIView):
    queryset = UserUpload.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserUpload.objects.filter(user=self.request.user)
    
class UserStatisticsView(generics.ListAPIView):
    def get(self, request, format=None):
        user = request.user

        # Get the date range for the past 7 days
        end_date = now().date()
        start_date = end_date - timedelta(days=6)

        # Aggregate srs_uploads for the past 7 days
        srs_uploads = (
            UserUpload.objects.filter(user=user, uploaded_at__date__range=(start_date, end_date))
            .values('uploaded_at__date')
            .annotate(number_of_uploads=Count('id'))
            .order_by('uploaded_at__date')
        )
        print(srs_uploads)

        # Ensure 7 days of data
        date_dict = {start_date + timedelta(days=i): 0 for i in range(7)}
        for entry in srs_uploads:
            date_dict[entry['uploaded_at__date']] = entry['number_of_uploads']

        srs_uploads_list = [{'date': date.isoformat(), 'number_Of_uploads': count} for date, count in date_dict.items()]

        # Total uploads
        total_uploads = UserUpload.objects.filter(user=user).count()

        # Preprocessed SRS documents (unique by user_upload)
        preprocessed_srs_docs = TextProcessing.objects.filter(user_upload__user=user).values('user_upload_id').distinct().count()

        # LDA and LSA entries
        lda_entries = LdaTopicModelling.objects.filter(text_processing__user_upload__user=user).count()
        lsa_entries = LsaTopicModelling.objects.filter(text_processing__user_upload__user=user).count()

        # Pending entries calculation
        all_uploads = UserUpload.objects.filter(user=user).values_list('id', flat=True)
        preprocessed_uploads = TextProcessing.objects.filter(user_upload__user=user).values_list('user_upload_id', flat=True).distinct()
        lda_processed = LdaTopicModelling.objects.filter(text_processing__user_upload__user=user).values_list('text_processing__user_upload_id', flat=True).distinct()
        lsa_processed = LsaTopicModelling.objects.filter(text_processing__user_upload__user=user).values_list('text_processing__user_upload_id', flat=True).distinct()
        unprocessed_uploads = set(all_uploads) - set(preprocessed_uploads)
        unmodeled_preprocessed = set(preprocessed_uploads) - (set(lda_processed) & set(lsa_processed))
        pending_entries = len(unprocessed_uploads) + len(unmodeled_preprocessed)


        # Critical vulnerabilities calculation
        critical_vulnerabilities = 0
        lda_critical_vulnerabilities = LdaTopicModelling.objects.filter(
            text_processing__user_upload__user=user
        ).values_list('results', flat=True)
        lsa_critical_vulnerabilities = LsaTopicModelling.objects.filter(
            text_processing__user_upload__user=user
        ).values_list('results', flat=True)
        
        for results in lda_critical_vulnerabilities:
            if results:
                critical_vulnerabilities += sum(1 for item in results if item['coherence'] >= 0.5)

        for results in lsa_critical_vulnerabilities:
            if results:
                critical_vulnerabilities += sum(1 for item in results if item['coherence'] >= 0.5)

        # Prepare response data
        response_data = {
            'srs_uploads': srs_uploads_list,
            'total_uploads': total_uploads,
            'preprocessed_srs_docs': preprocessed_srs_docs,
            'lda_entries': lda_entries,
            'lsa_entries': lsa_entries,
            'pending_entries': pending_entries,
            'critical_vulnerabilities': critical_vulnerabilities,
        }

        # Serialize the response data
        serializer = UserStatisticsSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
