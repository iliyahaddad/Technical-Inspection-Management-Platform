from django.contrib import admin
from apps.documents.models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ["sha256", "created_at"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "client", "project", "vendor", "uploaded_by", "is_confidential", "created_at"]
    list_filter = ["is_confidential", "document_type", "client", "vendor"]
    search_fields = ["title", "sha256", "client__name", "project__name", "vendor__name"]
    readonly_fields = ["sha256", "created_at", "updated_at"]
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ["document", "version_number", "uploaded_by", "created_at"]
    readonly_fields = ["sha256", "created_at"]
