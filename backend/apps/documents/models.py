from django.conf import settings
from django.db import models
from apps.documents.validators import validate_upload


class Document(models.Model):
    """Tenant-owned document metadata; every document belongs to one tenant context."""
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=64, blank=True)
    client = models.ForeignKey("clients.Client", null=True, blank=True, on_delete=models.CASCADE, related_name="documents")
    project = models.ForeignKey("projects.Project", null=True, blank=True, on_delete=models.CASCADE, related_name="documents")
    vendor = models.ForeignKey("projects.Vendor", null=True, blank=True, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_documents")
    file = models.FileField(upload_to="documents/%Y/%m/", validators=[validate_upload])
    sha256 = models.CharField(max_length=64, blank=True, editable=False)
    is_confidential = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["client", "created_at"]), models.Index(fields=["project", "created_at"]), models.Index(fields=["vendor", "created_at"])]
        constraints = [models.CheckConstraint(condition=(models.Q(client__isnull=False) | models.Q(project__isnull=False) | models.Q(vendor__isnull=False)), name="document_has_tenant_owner")]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.project_id and self.client_id and self.project.client_id != self.client_id:
            raise ValidationError({"client": "Client must match the selected project."})
        if not (self.client_id or self.project_id or self.vendor_id):
            raise ValidationError("A document must be linked to a client, project, or vendor.")

    def __str__(self):
        return self.title


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to="document_versions/%Y/%m/", validators=[validate_upload])
    sha256 = models.CharField(max_length=64, blank=True, editable=False)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_document_versions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        constraints = [models.UniqueConstraint(fields=["document", "version_number"], name="unique_document_version_number")]

    def __str__(self):
        return f"{self.document_id} v{self.version_number}"
