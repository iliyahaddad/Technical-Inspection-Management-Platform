from rest_framework import serializers
from .models import AuditEvent

class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ['id', 'user', 'action', 'object_type', 'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent', 'timestamp']
        read_only_fields = ['id', 'timestamp']
