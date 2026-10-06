import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, to_email, subject, message, html_message=None):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return {'status': 'sent', 'to': to_email}
    except Exception as exc:
        raise self.retry(exc=exc)


def _notify(user, title, message):
    """Create the in-app notification and queue the e-mail after the surrounding transaction commits.

    Strings must be plain ``str`` (not lazy translations) so Celery can JSON-serialise them; the
    previous implementation passed lazy strings and every e-mail silently failed.
    """
    if user is None:
        return
    title, message = str(title), str(message)
    try:
        from apps.notifications.models import Notification
        Notification.objects.create(user=user, title=title[:255], message=message)
        if user.email:
            transaction.on_commit(lambda: send_email_notification.delay(user.email, title, message))
    except Exception:
        logger.exception('notification delivery failed for user %s', getattr(user, 'pk', None))


def notify_assignment(assignment):
    request = assignment.notification.inspection_request
    _notify(
        assignment.inspector.user,
        _('New Assignment Notification'),
        _('You have been assigned to inspection request %(request)s for project %(project)s. Please review and accept.')
        % {'request': request.request_number, 'project': request.project.name},
    )


def notify_report_approval(report):
    # At submission time ``reviewed_by`` is empty. Notify the coordinator
    # who proposed the inspection instead of silently dropping the notification.
    reviewer = report.reviewed_by
    if reviewer is None:
        try:
            reviewer = report.inspection_visit.assignment.proposed_by
        except AttributeError:
            reviewer = None
    _notify(
        reviewer,
        _('Report Requires Review'),
        _('Report %(report)s requires your review. Please check the report and provide feedback.')
        % {'report': report.report_number},
    )


def notify_ncr_creation(ncr):
    project = ncr.inspection_visit.assignment.notification.inspection_request.project.name
    _notify(
        ncr.responsible_party,
        _('NCR Created - Action Required'),
        _('NCR %(ncr)s has been created for project %(project)s. Severity: %(severity)s. Please review and take corrective action.')
        % {'ncr': ncr.ncr_number, 'project': project, 'severity': ncr.severity},
    )


def notify_certificate_expiry(inspector):
    _notify(
        inspector.user,
        _('Certificate Expiry Alert'),
        _('One or more of your certificates are approaching expiry. Please renew them to maintain your inspection eligibility.'),
    )
