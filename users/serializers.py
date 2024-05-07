from rest_framework import serializers
from .models import CustomUser, UserUpload

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUpload
        fields = ['id', 'user_id', 'document', 'uploaded_at', 'document_name']