from rest_framework import serializers
from .models import Document, Category, ShareLink

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_url = serializers.FileField(source='file', read_only=True)
    is_near_expiry = serializers.BooleanField(read_only=True)

    class Meta:
        model = Document
        fields = ('id', 'title', 'category', 'category_name', 'file', 'file_url', 'file_type', 'file_size', 'uploaded_at', 'is_encrypted', 'expiry_date', 'security_level', 'is_near_expiry', 'file_hash')
        read_only_fields = ('file_type', 'file_size', 'uploaded_at', 'is_near_expiry', 'file_hash')

    def validate_file(self, value):
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("Unsupported file extension. Only PDF and Images are allowed.")
        
        if value.size > 5 * 1024 * 1024: # 5MB limit
            raise serializers.ValidationError("File size too large. Maximum limit is 5MB.")
        return value

    def create(self, validated_data):
        file = validated_data.get('file')
        if file:
            validated_data['file_type'] = file.content_type
            validated_data['file_size'] = file.size
        return super().create(validated_data)

class ShareLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareLink
        fields = ('id', 'document', 'token', 'created_at', 'expires_at', 'views_count', 'is_active', 'password')
        read_only_fields = ('token', 'created_at', 'views_count')
        extra_kwargs = {'password': {'write_only': True}}
