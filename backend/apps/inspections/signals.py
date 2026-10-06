from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.projects.services import DocumentNumberingService

@receiver(pre_save, sender='inspections.InspectionRequest')
def set_request_number(sender, instance, **kwargs):
    if not instance.request_number:
        instance.request_number = DocumentNumberingService.next_request_number()

@receiver(pre_save, sender='inspections.InspectionNotification')
def set_notification_number(sender, instance, **kwargs):
    if not instance.notification_number:
        instance.notification_number = DocumentNumberingService.next_notification_number()
