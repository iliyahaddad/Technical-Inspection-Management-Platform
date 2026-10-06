from django.db import models
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    client_code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=64, blank=True)
    tax_number = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name']), models.Index(fields=['is_active']), models.Index(fields=['client_code'])]

    def __str__(self):
        return f'{self.client_code} - {self.name}'

class ClientUser(models.Model):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('requester', _('Requester')),
        ('approver', _('Approver')),
    ]
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='client_links')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'client')
        indexes = [models.Index(fields=['client', 'role'])]

    def __str__(self):
        return f'{self.user} @ {self.client} ({self.role})'
