from rest_framework import serializers
from apps.documents.models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ["id", "document", "version_number", "file", "sha256", "notes", "uploaded_by", "created_at"]
        read_only_fields = ["id", "document", "version_number", "sha256", "uploaded_by", "created_at"]
        extra_kwargs = {"file": {"write_only": True}}


class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ["id", "title", "document_type", "client", "project", "vendor", "uploaded_by", "file", "sha256", "is_confidential", "versions", "created_at", "updated_at"]
        read_only_fields = ["id", "uploaded_by", "sha256", "created_at", "updated_at", "versions"]
        extra_kwargs = {"file": {"write_only": True}}

    def validate(self, attrs):
        project = attrs.get("project")
        client = attrs.get("client")
        if project and client and project.client_id != client.pk:
            raise serializers.ValidationError({"client": "Client must match the selected project."})
        if not (project or client or attrs.get("vendor")):
            raise serializers.ValidationError("Link the document to a client, project, or vendor.")
        return attrs
