from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    """Audit records are append-only: no add/change/delete through the admin."""
    list_display = ["timestamp", "user", "action", "object_type", "object_id", "object_repr", "ip_address"]
    list_filter = ["action", "object_type", "timestamp"]
    search_fields = ["object_repr", "object_id", "user__email"]
    readonly_fields = [f.name for f in AuditEvent._meta.fields]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
