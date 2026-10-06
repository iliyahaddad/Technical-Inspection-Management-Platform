from django.contrib import admin
from apps.projects.models import Project, Contract, ContractRevision, Vendor, VendorUser, Location, PurchaseOrder

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_code', 'name', 'client', 'status', 'project_manager']
    list_filter = ['status', 'client']
    search_fields = ['project_code', 'name']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'project', 'contract_type', 'status', 'start_date', 'end_date']
    list_filter = ['contract_type', 'status']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'contact_phone', 'is_active']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'is_active']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'project', 'vendor', 'issue_date']


@admin.register(VendorUser)
class VendorUserAdmin(admin.ModelAdmin):
    list_display = ["vendor", "user", "role", "is_active", "created_at"]
    list_filter = ["role", "is_active", "vendor"]
    search_fields = ["vendor__name", "user__email", "user__first_name", "user__last_name"]
