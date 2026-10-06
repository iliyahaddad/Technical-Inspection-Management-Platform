from django.db import models
from django.utils.translation import gettext_lazy as _

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VendorUser(models.Model):
    ROLE_CHOICES = [("admin", "Vendor Administrator"), ("representative", "Vendor Representative"), ("viewer", "Read Only")]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="user_links")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="vendor_links")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="representative")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["vendor", "user"], name="unique_vendor_user_link")]
        indexes = [models.Index(fields=["user", "is_active"])]

    def __str__(self):
        return f"{self.user} @ {self.vendor} ({self.role})"


class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=64)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='IRR')
    issue_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'po_number')

    def __str__(self):
        return self.po_number

class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('closed', _('Closed')),
    ]
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='projects')
    project_code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_manager = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    contract_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='IRR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['client', 'status']), models.Index(fields=['project_code'])]

    def __str__(self):
        return f'{self.project_code} - {self.name}'

class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('person_day', _('Person Day')),
        ('fixed_visit', _('Fixed Visit')),
        ('milestone', _('Milestone')),
        ('mixed', _('Mixed')),
    ]
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('terminated', _('Terminated')),
    ]
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contract_type = models.CharField(max_length=32, choices=CONTRACT_TYPE_CHOICES)
    total_value = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'contract_number')
        indexes = [models.Index(fields=['project', 'status'])]

    def __str__(self):
        return f'{self.contract_number} ({self.project.project_code})'

class ContractRevision(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.CharField(max_length=32)
    change_description = models.TextField()
    effective_date = models.DateField()
    supporting_document = models.CharField(max_length=1024, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('contract', 'revision_number')
