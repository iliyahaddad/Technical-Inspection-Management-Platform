import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-certificate-expiry': {
        'task': 'apps.inspections.tasks.check_certificate_expiry',
        'schedule': crontab(hour=6, minute=0),
    },
    'check-overdue-reports': {
        'task': 'apps.reports.tasks.check_overdue_reports',
        'schedule': crontab(hour=7, minute=0),
    },
    'check-ncr-overdue': {
        'task': 'apps.reports.tasks.check_ncr_overdue',
        'schedule': crontab(hour=7, minute=30),
    },
}
