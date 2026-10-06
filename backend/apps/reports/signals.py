from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.projects.services import DocumentNumberingService

@receiver(pre_save, sender='reports.InspectionReport')
def set_report_number(sender, instance, **kwargs):
    if not instance.report_number:
        instance.report_number = DocumentNumberingService.next_report_number()

@receiver(pre_save, sender='reports.NCR')
def set_ncr_number(sender, instance, **kwargs):
    if not instance.ncr_number:
        instance.ncr_number = DocumentNumberingService.next_ncr_number()

@receiver(pre_save, sender='reports.ReleaseNote')
def set_release_note_number(sender, instance, **kwargs):
    if not instance.release_number:
        instance.release_number = DocumentNumberingService.next_release_note_number()
