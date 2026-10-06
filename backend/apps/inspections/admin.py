from django.contrib import admin
from apps.inspections.models import InspectionRequest, RequestItem

@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'project', 'status', 'priority', 'discipline', 'submitted_by', 'created_at']
    list_filter = ['status', 'priority', 'discipline']
    search_fields = ['request_number', 'project__project_code']

@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ['request', 'item_number', 'description', 'quantity', 'unit']
    list_filter = ['request']
