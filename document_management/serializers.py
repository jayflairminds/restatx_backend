from rest_framework import serializers
from .models import *

class DocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source="document_detail.name", read_only=True)
    document_type = serializers.CharField(source="document_detail.type", read_only=True)
    document_type_id = serializers.CharField(source="document_detail.document_type_id", read_only=True)    
    class Meta:
        model = Document
        fields = "__all__"

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"