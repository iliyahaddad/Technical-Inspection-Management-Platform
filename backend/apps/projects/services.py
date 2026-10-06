import secrets
from django.db import transaction
from django.utils import timezone
from apps.projects.models import Project
from apps.inspections.models import InspectionRequest, InspectionNotification
from apps.reports.models import InspectionReport, NCR, ReleaseNote
from apps.mts.models import FinancialStatement, InvoiceReference
from apps.clients.models import Client

class DocumentNumberingService:
    @staticmethod
    def generate(prefix: str, model_class, field: str = 'document_number', padding: int = 4) -> str:
        today = timezone.now()
        date_part = today.strftime('%Y%m%d')
        random_part = secrets.token_hex(3).upper()
        return f'{prefix}-{date_part}-{random_part}'

    @staticmethod
    def next_client_code() -> str:
        last = Client.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        return f'CLI-{seq:05d}'

    @staticmethod
    def next_project_code(prefix: str = 'PRJ') -> str:
        last = Project.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        return f'{prefix}-{seq:05d}'

    @staticmethod
    def next_request_number() -> str:
        return DocumentNumberingService.generate('REQ', InspectionRequest)

    @staticmethod
    def next_notification_number() -> str:
        return DocumentNumberingService.generate('ITN', InspectionNotification)

    @staticmethod
    def next_report_number() -> str:
        return DocumentNumberingService.generate('RPT', InspectionReport)

    @staticmethod
    def next_ncr_number() -> str:
        return DocumentNumberingService.generate('NCR', NCR)

    @staticmethod
    def next_release_note_number() -> str:
        return DocumentNumberingService.generate('REL', ReleaseNote)

    @staticmethod
    def next_statement_number() -> str:
        return DocumentNumberingService.generate('STMT', FinancialStatement)

    @staticmethod
    def next_invoice_number() -> str:
        return DocumentNumberingService.generate('INV', InvoiceReference)
