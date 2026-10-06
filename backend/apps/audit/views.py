from rest_framework import viewsets

from config.access_control import RoleAndScopePermission, ScopedAccessMixin

from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventViewSet(ScopedAccessMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only audit trail for administrators, auditors, GM and quality managers."""
    queryset = AuditEvent.objects.select_related("user")
    serializer_class = AuditEventSerializer
    permission_classes = [RoleAndScopePermission]
    filterset_fields = ["action", "object_type", "object_id", "user"]
    search_fields = ["object_repr", "object_id", "user__email"]
    ordering_fields = ["timestamp"]
