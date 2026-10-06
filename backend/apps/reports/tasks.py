import logging
from datetime import timedelta

from celery import shared_task
from django.core.mail import mail_admins
from django.utils import timezone

logger = logging.getLogger(__name__)

REPORT_REVIEW_SLA_DAYS = 7


@shared_task
def check_overdue_reports():
    """Reports waiting for review longer than the SLA."""
    from apps.reports.models import InspectionReport

    overdue = InspectionReport.objects.filter(
        status='submitted', submitted_at__lt=timezone.now() - timedelta(days=REPORT_REVIEW_SLA_DAYS)
    )
    count = overdue.count()
    if count:
        mail_admins('Overdue Reports Alert', f'{count} reports overdue for review.', fail_silently=True)
    return count


@shared_task
def check_ncr_overdue():
    """Open/in-progress NCRs past their target completion date."""
    from apps.reports.models import NCR

    overdue = NCR.objects.filter(
        status__in=['open', 'in_progress'], target_completion_date__lt=timezone.now().date()
    )
    count = overdue.count()
    if count:
        mail_admins('NCR Overdue Alert', f'{count} NCRs overdue.', fail_silently=True)
    return count
