from apps.documents.validators import validate_upload
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
import secrets

class InspectionRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('under_review', _('Under Review')),
        ('clarification_required', _('Clarification Required')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('ready_for_scheduling', _('Ready for Scheduling')),
    ]
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    request_number = models.CharField(max_length=64, unique=True)
    revision = models.PositiveIntegerField(default=1)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='inspection_requests')
    submitted_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='submitted_requests')
    contract = models.ForeignKey('projects.Contract', on_delete=models.SET_NULL, null=True, blank=True)
    purchase_order = models.ForeignKey('projects.PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey('projects.Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey('projects.Location', on_delete=models.SET_NULL, null=True, blank=True)
    requested_inspection_date = models.DateTimeField(null=True, blank=True)
    discipline = models.CharField(max_length=64)
    inspection_type = models.CharField(max_length=64)
    inspection_level = models.CharField(max_length=16, blank=True)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default='normal')
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['project', 'status']), models.Index(fields=['request_number'])]

    def __str__(self):
        return self.request_number

@receiver(pre_save, sender='inspections.InspectionRequest')
def generate_request_number(sender, instance, **kwargs):
    if not instance.request_number:
        instance.request_number = f'IRF-{secrets.token_hex(4).upper()}'

class RequestItem(models.Model):
    request = models.ForeignKey(InspectionRequest, on_delete=models.CASCADE, related_name='items')
    item_number = models.PositiveIntegerField()
    equipment_tag = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=255)
    material_type = models.CharField(max_length=128, blank=True)
    specification = models.CharField(max_length=255, blank=True)
    drawing_reference = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=32)
    previously_inspected_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    requested_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('request', 'item_number')
        ordering = ['request', 'item_number']

class InspectionNotification(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('issued', _('Issued')),
        ('acknowledged', _('Acknowledged')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    notification_number = models.CharField(max_length=64, unique=True)
    revision = models.PositiveIntegerField(default=1)
    inspection_request = models.ForeignKey(InspectionRequest, on_delete=models.PROTECT, related_name='notifications')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='notifications')
    vendor = models.ForeignKey('projects.Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey('projects.Location', on_delete=models.SET_NULL, null=True, blank=True)
    inspection_date = models.DateTimeField()
    inspection_type = models.CharField(max_length=64)
    itp = models.ForeignKey('ITP', on_delete=models.SET_NULL, null=True, blank=True)
    notice_period_days = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    issued_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='issued_notifications')
    acknowledged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_notifications')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['project', 'status']), models.Index(fields=['notification_number'])]

    def __str__(self):
        return self.notification_number

@receiver(pre_save, sender='inspections.InspectionNotification')
def generate_notification_number(sender, instance, **kwargs):
    if not instance.notification_number:
        instance.notification_number = f'ITN-{secrets.token_hex(4).upper()}'

class ITP(models.Model):
    itp_number = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    revision = models.CharField(max_length=32, default='A')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='itps')
    applicable_standard = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.itp_number} Rev {self.revision}'

class ITPActivity(models.Model):
    INTERVENTION_TYPE_CHOICES = [
        ('H', _('Hold Point')),
        ('W', _('Witness Point')),
        ('SW', _('Spot Witness')),
        ('M', _('Monitoring')),
        ('R', _('Document Review')),
    ]
    itp = models.ForeignKey(ITP, on_delete=models.CASCADE, related_name='activities')
    activity_number = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    intervention_type = models.CharField(max_length=8, choices=INTERVENTION_TYPE_CHOICES)
    relevant_drawing = models.CharField(max_length=255, blank=True)
    applicable_standard = models.CharField(max_length=255, blank=True)
    acceptance_criteria = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)

    class Meta:
        unique_together = ('itp', 'activity_number')

class InspectorProfile(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('employee', _('Employee')),
        ('contractor', _('Contractor')),
    ]
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='inspector_profile')
    employee_number = models.CharField(max_length=64, blank=True)
    employment_type = models.CharField(max_length=32, choices=EMPLOYMENT_TYPE_CHOICES, default='contractor')
    disciplines = models.JSONField(default=list)
    specializations = models.JSONField(default=list, blank=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    geographic_location = models.CharField(max_length=128, blank=True)
    coverage_areas = models.JSONField(default=list, blank=True)
    travel_preferences = models.JSONField(default=dict, blank=True)
    conflict_of_interest_declared = models.BooleanField(default=False)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.employment_type})'

class Certificate(models.Model):
    inspector = models.ForeignKey(InspectorProfile, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=255)
    issuing_body = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    certificate_number = models.CharField(max_length=128, blank=True)
    file = models.FileField(upload_to='certificates/%Y/%m/', blank=True, validators=[validate_upload])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.inspector.user.get_full_name()}'

class Availability(models.Model):
    inspector = models.ForeignKey(InspectorProfile, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('inspector', 'date')
        indexes = [models.Index(fields=['inspector', 'date'])]

class Assignment(models.Model):
    STATUS_CHOICES = [
        ('proposed', _('Proposed')),
        ('approved', _('Approved')),
        ('notified', _('Notified')),
        ('accepted', _('Accepted')),
        ('declined', _('Declined')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    notification = models.ForeignKey(InspectionNotification, on_delete=models.PROTECT, related_name='assignments')
    inspector = models.ForeignKey(InspectorProfile, on_delete=models.PROTECT, related_name='assignments')
    proposed_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='proposed_assignments')
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_assignments')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='proposed')
    proposed_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['inspector', 'status']), models.Index(fields=['notification'])]

class InspectionVisit(models.Model):
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('postponed', _('Postponed')),
        ('cancelled', _('Cancelled')),
    ]
    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, related_name='visits')
    visit_number = models.CharField(max_length=64, unique=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey('projects.Location', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.visit_number

@receiver(pre_save, sender='inspections.InspectionVisit')
def generate_visit_number(sender, instance, **kwargs):
    if not instance.visit_number:
        instance.visit_number = f'VIS-{secrets.token_hex(4).upper()}'
