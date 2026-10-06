import logging
from datetime import timedelta

from celery import shared_task
from django.core.mail import mail_admins
from django.utils import timezone

logger = logging.getLogger(__name__)

CERTIFICATE_WARNING_DAYS = 30


@shared_task
def check_certificate_expiry():
    """Alert admins and the affected inspectors about certificates expiring within 30 days."""
    from apps.inspections.models import Certificate
    from apps.notifications.tasks import notify_certificate_expiry

    today = timezone.now().date()
    expiring = Certificate.objects.filter(
        expiry_date__lte=today + timedelta(days=CERTIFICATE_WARNING_DAYS), expiry_date__gte=today
    ).select_related('inspector__user')
    count = expiring.count()
    if not count:
        return 0
    for inspector in {c.inspector for c in expiring}:
        notify_certificate_expiry(inspector)
    mail_admins('Certificate Expiry Alert', f'{count} certificates expiring within {CERTIFICATE_WARNING_DAYS} days.', fail_silently=True)
    return count
