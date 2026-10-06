from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.projects.services import DocumentNumberingService

@receiver(pre_save, sender='mts.FinancialStatement')
def set_statement_number(sender, instance, **kwargs):
    if not instance.statement_number:
        instance.statement_number = DocumentNumberingService.next_statement_number()

@receiver(pre_save, sender='mts.InvoiceReference')
def set_invoice_number(sender, instance, **kwargs):
    if not instance.invoice_number:
        instance.invoice_number = DocumentNumberingService.next_invoice_number()
