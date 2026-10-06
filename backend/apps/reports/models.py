from apps.documents.validators import validate_upload
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
import secrets
from apps.inspections.models import InspectionVisit

class InspectionReport(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('under_review', _('Under Review')),
        ('revision_required', _('Revision Required')),
        ('approved', _('Approved')),
        ('issued', _('Issued')),
    ]
    report_number = models.CharField(max_length=64, unique=True)
    revision = models.PositiveIntegerField(default=1)
    inspection_visit = models.ForeignKey(InspectionVisit, on_delete=models.PROTECT, related_name='reports')
    template_version = models.ForeignKey('reports.TemplateVersion', on_delete=models.SET_NULL, null=True, blank=True)
    submitted_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='submitted_reports')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    scope = models.TextField(blank=True)
    inspected_qty = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    accepted_qty = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    rejected_qty = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    remaining_qty = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    instruments_used = models.JSONField(default=list, blank=True)
    narrative = models.TextField(blank=True)
    deviations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_reports')
    content_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['inspection_visit', 'status']), models.Index(fields=['report_number'])]

    def __str__(self):
        return self.report_number

@receiver(pre_save, sender='reports.InspectionReport')
def generate_report_number(sender, instance, **kwargs):
    if not instance.report_number:
        instance.report_number = f'RPT-{secrets.token_hex(4).upper()}'

class ReportRevision(models.Model):
    report = models.ForeignKey(InspectionReport, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.PositiveIntegerField()
    content = models.JSONField()
    content_hash = models.CharField(max_length=64)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('report', 'revision_number')
        ordering = ['-revision_number']

class ChecklistAnswer(models.Model):
    report_revision = models.ForeignKey(ReportRevision, on_delete=models.CASCADE, related_name='checklist_answers')
    activity_id = models.CharField(max_length=64)
    answer = models.CharField(max_length=32)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Measurement(models.Model):
    report_revision = models.ForeignKey(ReportRevision, on_delete=models.CASCADE, related_name='measurements')
    parameter = models.CharField(max_length=255)
    value = models.CharField(max_length=128)
    unit = models.CharField(max_length=32, blank=True)
    tolerance = models.CharField(max_length=128, blank=True)
    result = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    report_revision = models.ForeignKey(ReportRevision, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/', validators=[validate_upload])
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Instrument(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=128, unique=True)
    calibration_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    certificate_number = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.serial_number})'

class InspectionTemplate(models.Model):
    name = models.CharField(max_length=255)
    discipline = models.CharField(max_length=64)
    version = models.CharField(max_length=32, default='1.0')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} v{self.version}'

class TemplateVersion(models.Model):
    template = models.ForeignKey(InspectionTemplate, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=32)
    schema = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('template', 'version_number')

class NCR(models.Model):
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('verification', _('Verification')),
        ('closed', _('Closed')),
        ('waived', _('Waived')),
    ]
    SEVERITY_CHOICES = [
        ('minor', _('Minor')),
        ('major', _('Major')),
        ('critical', _('Critical')),
    ]
    ncr_number = models.CharField(max_length=64, unique=True)
    inspection_visit = models.ForeignKey(InspectionVisit, on_delete=models.SET_NULL, null=True, blank=True, related_name='ncrs')
    report_revision = models.ForeignKey(ReportRevision, on_delete=models.SET_NULL, null=True, blank=True, related_name='ncrs')
    itp_activity = models.ForeignKey('inspections.ITPActivity', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    requirement_reference = models.TextField(blank=True)
    evidence = models.JSONField(default=list, blank=True)
    severity = models.CharField(max_length=32, choices=SEVERITY_CHOICES, default='minor')
    responsible_party = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='responsible_ncrs')
    proposed_corrective_action = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='open')
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_ncrs')
    closure_notes = models.TextField(blank=True)  # verification evidence or waiver justification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ncr_number

@receiver(pre_save, sender='reports.NCR')
def generate_ncr_number(sender, instance, **kwargs):
    if not instance.ncr_number:
        instance.ncr_number = f'NCR-{secrets.token_hex(4).upper()}'

class CorrectiveAction(models.Model):
    ncr = models.ForeignKey(NCR, on_delete=models.CASCADE, related_name='corrective_actions')
    description = models.TextField()
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    evidence = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReleaseNote(models.Model):
    release_number = models.CharField(max_length=64, unique=True)
    inspection_visit = models.ForeignKey(InspectionVisit, on_delete=models.PROTECT, related_name='release_notes')
    released_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='released_notes')
    notes = models.TextField()
    is_final = models.BooleanField(default=False)
    released_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.release_number

@receiver(pre_save, sender='reports.ReleaseNote')
def generate_release_number(sender, instance, **kwargs):
    if not instance.release_number:
        instance.release_number = f'REL-{secrets.token_hex(4).upper()}'
