from rest_framework import serializers
from .models import CustomUser, UserUpload

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUpload
        fields = ['id', 'user_id', 'document', 'uploaded_at', 'document_name', 'status']
        read_only_fields = ['document_name']