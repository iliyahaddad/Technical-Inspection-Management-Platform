from apps.documents.validators import validate_upload
from django.db import models
from django.utils.translation import gettext_lazy as _

class Timesheet(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('locked', _('Locked')),
    ]
    inspector = models.ForeignKey('inspections.InspectorProfile', on_delete=models.PROTECT, related_name='timesheets')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='timesheets')
    assignment = models.ForeignKey('inspections.Assignment', on_delete=models.SET_NULL, null=True, blank=True)
    month = models.DateField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_timesheets')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('inspector', 'project', 'month')
        indexes = [models.Index(fields=['inspector', 'project', 'month'])]

class TimesheetEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries')
    work_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    break_duration = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2)
    travel_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    waiting_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    visit = models.ForeignKey('inspections.InspectionVisit', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('timesheet', 'work_date')
        indexes = [models.Index(fields=['timesheet', 'work_date'])]

class Expense(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    inspector = models.ForeignKey('inspections.InspectorProfile', on_delete=models.PROTECT, related_name='expenses')
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='expenses')
    assignment = models.ForeignKey('inspections.Assignment', on_delete=models.SET_NULL, null=True, blank=True)
    expense_date = models.DateField()
    category = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='IRR')
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to='receipts/%Y/%m/', blank=True, validators=[validate_upload])
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['inspector', 'project', 'expense_date'])]

class RateCard(models.Model):
    BILLING_MODEL_CHOICES = [
        ('person_day', _('Person Day')),
        ('fixed_visit', _('Fixed Visit')),
        ('milestone', _('Milestone')),
        ('reimbursable', _('Reimbursable')),
    ]
    contract = models.ForeignKey('projects.Contract', on_delete=models.CASCADE, related_name='rate_cards')
    name = models.CharField(max_length=255)
    billing_model = models.CharField(max_length=32, choices=BILLING_MODEL_CHOICES)
    currency = models.CharField(max_length=3)
    region = models.CharField(max_length=128, blank=True)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.contract.contract_number})'

class RateRevision(models.Model):
    rate_card = models.ForeignKey(RateCard, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.CharField(max_length=32)
    rate_type = models.CharField(max_length=64)
    unit = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=3)
    min_chargeable_unit = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_multiplier = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    travel_multiplier = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rate_card', 'revision_number')

class CurrencyRate(models.Model):
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['from_currency', 'to_currency', 'effective_date'])]

class FinancialStatement(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('approved', _('Approved')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('partial', _('Partial')),
    ]
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='financial_statements')
    statement_number = models.CharField(max_length=64, unique=True)
    period_start = models.DateField()
    period_end = models.DateField()
    currency = models.CharField(max_length=3)
    total_billable = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_invoiced = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    current_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_due = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_statements')
    approved_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statement_number

class StatementLine(models.Model):
    statement = models.ForeignKey(FinancialStatement, on_delete=models.CASCADE, related_name='lines')
    line_type = models.CharField(max_length=32)
    reference_type = models.CharField(max_length=64, blank=True)
    reference_id = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    unit_rate = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['statement', 'line_type'])]

class InvoiceReference(models.Model):
    statement = models.ForeignKey(FinancialStatement, on_delete=models.CASCADE, related_name='invoice_references')
    invoice_number = models.CharField(max_length=64)
    invoice_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentRecord(models.Model):
    statement = models.ForeignKey(FinancialStatement, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    reference = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SignatureRecord(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='signatures')
    document_type = models.CharField(max_length=64)
    document_id = models.CharField(max_length=64)
    revision = models.PositiveIntegerField()
    image = models.TextField()  # base64 data-URI of the captured signature (exceeds 1024 chars)
    content_hash = models.CharField(max_length=64)
    ip_address = models.CharField(max_length=45, blank=True)
    user_agent = models.TextField(blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['document_type', 'document_id', 'revision'])]

class ApprovalRecord(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='approvals')
    object_type = models.CharField(max_length=128)
    object_id = models.CharField(max_length=64)
    action = models.CharField(max_length=64)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['object_type', 'object_id'])]

class CostLedger(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('timesheet', _('Timesheet')),
        ('expense', _('Expense')),
        ('invoice', _('Invoice')),
    ]
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='cost_ledger')
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPE_CHOICES)
    source_id = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    cost_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['project', 'cost_date']), models.Index(fields=['source_type', 'source_id'])]

