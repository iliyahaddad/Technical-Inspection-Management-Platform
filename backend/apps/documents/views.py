import hashlib

from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import Document, DocumentVersion
from apps.documents.pdf_generator import generate_financial_statement_pdf, generate_inspection_report_pdf
from apps.documents.responses import protected_file_response
from apps.documents.serializers import DocumentSerializer, DocumentVersionSerializer
from config.access_control import RoleAndScopePermission, ScopedAccessMixin, is_global_admin, scoped_queryset


def _sha256(fieldfile):
    digest = hashlib.sha256()
    fieldfile.open('rb')
    try:
        for chunk in fieldfile.chunks():
            digest.update(chunk)
    finally:
        fieldfile.close()
    return digest.hexdigest()


class DocumentViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Document.objects.select_related('client', 'project', 'vendor').prefetch_related('versions')
    serializer_class = DocumentSerializer
    permission_classes = [RoleAndScopePermission]
    http_method_names = ['get', 'post', 'head', 'options']
    filterset_fields = ['client', 'project', 'vendor', 'document_type', 'is_confidential']
    search_fields = ['title', 'document_type']

    def perform_create(self, serializer):
        user = self.request.user
        self._validate_related_scope(serializer)
        if not is_global_admin(user):
            vendor = serializer.validated_data.get('vendor')
            if vendor and not user.vendor_links.filter(vendor_id=vendor.pk, is_active=True).exists():
                raise PermissionDenied('Vendor is outside your tenant scope.')
        document = serializer.save(uploaded_by=user)
        document.sha256 = _sha256(document.file)
        document.save(update_fields=['sha256'])

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        document = self.get_object()
        return protected_file_response(document.file, document.title and f"{document.title}.{document.file.name.rsplit('.', 1)[-1]}")

    @action(detail=True, methods=['post'], url_path='new-version')
    def new_version(self, request, pk=None):
        """Upload a new revision of an existing document; earlier versions are kept immutable."""
        document = self.get_object()
        serializer = DocumentVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            last = document.versions.aggregate(m=Max('version_number'))['m'] or 0
            version = serializer.save(document=document, version_number=last + 1, uploaded_by=request.user)
            version.sha256 = _sha256(version.file)
            version.save(update_fields=['sha256'])
        return Response(DocumentVersionSerializer(version).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path=r'versions/(?P<version_number>\d+)/download')
    def download_version(self, request, pk=None, version_number=None):
        document = self.get_object()
        version = document.versions.filter(version_number=version_number).first()
        if version is None:
            return Response({'detail': 'Version not found.'}, status=status.HTTP_404_NOT_FOUND)
        return protected_file_response(version.file)


class InspectionReportPdfView(APIView):
    permission_model_label = 'reports.inspectionreport'
    permission_classes = [RoleAndScopePermission]

    def get(self, request, report_id):
        from apps.reports.models import InspectionReport
        report = scoped_queryset(request.user, InspectionReport.objects.all()).filter(id=report_id).select_related(
            'inspection_visit__assignment__notification__inspection_request__project__client',
            'inspection_visit__assignment__notification', 'submitted_by',
        ).first()
        if report is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        visit = report.inspection_visit
        notification = visit.assignment.notification if visit and visit.assignment else None
        irf = notification.inspection_request if notification else None
        findings = []
        revision = report.revisions.order_by('-revision_number').first()
        if revision is not None:
            for answer in revision.checklist_answers.all():
                findings.append({'description': f"{answer.activity_id}: {answer.remarks}".strip(': '), 'status': answer.answer})
            for m in revision.measurements.all():
                findings.append({'description': f"{m.parameter} = {m.value} {m.unit} ({m.tolerance})".strip(), 'status': m.result})
        for ncr in report.inspection_visit.ncrs.all() if visit else []:
            findings.append({'description': f"NCR {ncr.ncr_number}: {ncr.description}", 'status': ncr.get_severity_display()})
        data = {
            'report_number': report.report_number,
            'project_name': irf.project.name if irf else '',
            'client_name': irf.project.client.name if irf else '',
            'inspection_date': report.created_at.strftime('%Y-%m-%d') if report.created_at else '',
            'inspector_name': report.submitted_by.get_full_name() or report.submitted_by.email,
            'discipline': irf.discipline if irf else '',
            'inspection_type': notification.inspection_type if notification else '',
            'status': report.get_status_display(),
            'scope': report.scope,
            'narrative': report.narrative,
            'findings': findings,
            'content_hash': report.content_hash,
        }
        pdf_buffer = generate_inspection_report_pdf(data)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{report.report_number}.pdf"'
        response['Cache-Control'] = 'private, no-store'
        return response


class FinancialStatementPdfView(APIView):
    permission_model_label = 'mts.financialstatement'
    permission_classes = [RoleAndScopePermission]

    def get(self, request, statement_id):
        from apps.mts.models import FinancialStatement
        statement = scoped_queryset(request.user, FinancialStatement.objects.all()).filter(id=statement_id).select_related('project').first()
        if statement is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = {
            'statement_number': statement.statement_number,
            'project_name': statement.project.name,
            'period_start': str(statement.period_start),
            'period_end': str(statement.period_end),
            'currency': statement.currency,
            'status': statement.get_status_display(),
            'total_billable': float(statement.total_billable),
            'lines': [
                {'line_type': l.line_type, 'description': l.description, 'amount': float(l.amount), 'currency': l.currency}
                for l in statement.lines.all()
            ],
        }
        pdf_buffer = generate_financial_statement_pdf(data)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{statement.statement_number}.pdf"'
        response['Cache-Control'] = 'private, no-store'
        return response
