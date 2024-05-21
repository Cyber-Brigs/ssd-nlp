import os
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, UserUploadSerializer
from .models import UserUpload

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
        # Set current user and other metadata
        serializer.save(user=self.request.user)
        
class UserUploadListView(generics.ListAPIView):
    queryset = UserUpload.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserUpload.objects.filter(user=self.request.user)
