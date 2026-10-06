from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.projects.models import Project, Contract, PurchaseOrder
from apps.clients.models import Client
from apps.projects.services import DocumentNumberingService

@receiver(pre_save, sender=Client)
def set_client_code(sender, instance, **kwargs):
    if not instance.client_code:
        instance.client_code = DocumentNumberingService.next_client_code()

@receiver(pre_save, sender=Project)
def set_project_code(sender, instance, **kwargs):
    if not instance.project_code:
        instance.project_code = DocumentNumberingService.next_project_code()

@receiver(pre_save, sender=Contract)
def set_contract_number(sender, instance, **kwargs):
    if not instance.contract_number:
        instance.contract_number = DocumentNumberingService.generate('CON', Contract)

@receiver(pre_save, sender=PurchaseOrder)
def set_po_number(sender, instance, **kwargs):
    if not instance.po_number:
        instance.po_number = DocumentNumberingService.generate('PO', PurchaseOrder)
