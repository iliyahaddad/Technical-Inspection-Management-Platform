from config.access_control import ScopedAccessMixin, RoleAndScopePermission
from config.workflow import LockedStatusMixin, ChildLockMixin, TransitionMixin, forbid_self_review
from apps.documents.responses import protected_file_response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.reports.models import (
    InspectionReport,
    ReportRevision,
    ChecklistAnswer,
    Measurement,
    Attachment,
    Instrument,
    InspectionTemplate,
    TemplateVersion,
    NCR,
    CorrectiveAction,
    ReleaseNote,
)
from apps.reports.serializers import (
    InspectionReportSerializer,
    ReportRevisionSerializer,
    ChecklistAnswerSerializer,
    MeasurementSerializer,
    AttachmentSerializer,
    InstrumentSerializer,
    InspectionTemplateSerializer,
    TemplateVersionSerializer,
    NCRSerializer,
    CorrectiveActionSerializer,
    ReleaseNoteSerializer,
)


def report_digest(report):
    """SHA-256 over the substantive content of a report (header fields, checklist answers, measurements)."""
    import hashlib, json
    revisions = []
    for rev in report.revisions.order_by('revision_number'):
        revisions.append({
            'n': rev.revision_number,
            'content': rev.content,
            'answers': sorted((a.activity_id, a.answer, a.remarks) for a in rev.checklist_answers.all()),
            'measurements': sorted((m.parameter, m.value, m.unit, m.tolerance, m.result) for m in rev.measurements.all()),
        })
    payload = {
        'visit': report.inspection_visit_id, 'scope': report.scope, 'narrative': report.narrative,
        'deviations': report.deviations, 'recommendations': report.recommendations,
        'qty': [str(report.inspected_qty), str(report.accepted_qty), str(report.rejected_qty), str(report.remaining_qty)],
        'instruments': report.instruments_used, 'revisions': revisions,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8')).hexdigest()


REPORT_LOCKED = frozenset({'submitted', 'under_review', 'approved', 'issued'})


class ReportChildLockMixin:
    """Revisions, checklist answers, measurements and attachments belong to a report; once the report is
    submitted they are evidence and must not change (this also protects the content digest)."""
    report_path = 'report'  # lookup from the child to the InspectionReport

    def _report_of(self, obj):
        for part in self.report_path.split('__'):
            obj = getattr(obj, part)
        return obj

    def _guard(self, report):
        if report is not None and report.status in REPORT_LOCKED:
            from config.workflow import Conflict
            raise Conflict('The report is locked; its content can no longer be modified.')

    def perform_create(self, serializer):
        parent = serializer.validated_data.get(self.parent_field)
        self._guard(self._report_of_parent(parent))
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self._guard(self._report_of(serializer.instance))
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._guard(self._report_of(instance))
        super().perform_destroy(instance)

    def _report_of_parent(self, parent):
        if parent is None:
            return None
        return parent if parent.__class__.__name__ == 'InspectionReport' else parent.report


class InspectionReportViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'submitted', 'under_review', 'approved', 'issued'})
    queryset = InspectionReport.objects.all()
    serializer_class = InspectionReportSerializer
    permission_classes = [RoleAndScopePermission]

    @staticmethod
    def _snapshot(report):
        return {
            'scope': report.scope, 'narrative': report.narrative, 'deviations': report.deviations,
            'recommendations': report.recommendations,
            'inspected_qty': str(report.inspected_qty) if report.inspected_qty is not None else None,
            'accepted_qty': str(report.accepted_qty) if report.accepted_qty is not None else None,
            'rejected_qty': str(report.rejected_qty) if report.rejected_qty is not None else None,
            'remaining_qty': str(report.remaining_qty) if report.remaining_qty is not None else None,
            'instruments_used': report.instruments_used,
        }

    @staticmethod
    def _digest(content):
        import hashlib, json
        return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8')).hexdigest()

    def perform_create(self, serializer):
        from django.db import transaction
        self._validate_related_scope(serializer)
        with transaction.atomic():
            report = serializer.save(submitted_by=self.request.user, content_hash='')
            content = self._snapshot(report)
            digest = self._digest(content)
            ReportRevision.objects.create(
                report=report, revision_number=report.revision, content=content,
                content_hash=digest, created_by=self.request.user,
            )

    def perform_update(self, serializer):
        from django.db import transaction
        report = serializer.instance
        self._validate_related_scope(serializer)
        self._assert_unlocked(report)
        with transaction.atomic():
            was_revision_required = report.status == 'revision_required'
            report = serializer.save(
                status='draft' if was_revision_required else report.status,
                reviewed_by=None if was_revision_required else report.reviewed_by,
                reviewed_at=None if was_revision_required else report.reviewed_at,
                review_comments='' if was_revision_required else report.review_comments,
                content_hash='',
            )
            content = self._snapshot(report)
            digest = self._digest(content)
            if was_revision_required:
                report.revision += 1
                report.save(update_fields=['revision', 'content_hash', 'updated_at'])
                ReportRevision.objects.create(
                    report=report, revision_number=report.revision, content=content,
                    content_hash=digest, created_by=self.request.user,
                )
            else:
                latest = report.revisions.order_by('-revision_number').first()
                if latest is None:
                    ReportRevision.objects.create(
                        report=report, revision_number=report.revision, content=content,
                        content_hash=digest, created_by=self.request.user,
                    )
                else:
                    latest.content = content
                    latest.content_hash = digest
                    latest.save(update_fields=['content', 'content_hash'])

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'draft':
            return Response({'detail': 'Only draft reports can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'submitted'
        instance.submitted_by = request.user
        instance.submitted_at = timezone.now()
        instance.content_hash = report_digest(instance)
        instance.save()
        from apps.notifications.tasks import notify_report_approval
        notify_report_approval(instance)
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.status not in ['submitted', 'under_review']:
            return Response({'detail': 'Report must be submitted or under review.'}, status=status.HTTP_400_BAD_REQUEST)
        forbid_self_review(request, instance.submitted_by_id, 'report')
        if instance.content_hash and instance.content_hash != report_digest(instance):
            return Response({'detail': 'Report content changed after submission; return it for revision.'}, status=status.HTTP_409_CONFLICT)
        instance.status = 'approved'
        instance.reviewed_by = request.user
        instance.reviewed_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def return_for_revision(self, request, pk=None):
        instance = self.get_object()
        if instance.status not in ['submitted', 'under_review']:
            return Response({'detail': 'Report must be submitted or under review.'}, status=status.HTTP_400_BAD_REQUEST)
        forbid_self_review(request, instance.submitted_by_id, 'report')
        instance.status = 'revision_required'
        instance.reviewed_by = request.user
        instance.reviewed_at = timezone.now()
        instance.review_comments = request.data.get('comments', '')
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'approved':
            return Response({'detail': 'Only approved reports can be issued.'}, status=status.HTTP_400_BAD_REQUEST)
        if instance.content_hash and instance.content_hash != report_digest(instance):
            return Response({'detail': 'Report content changed after approval.'}, status=status.HTTP_409_CONFLICT)
        instance.status = 'issued'
        instance.issued_by = request.user
        instance.issued_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

class ReportRevisionViewSet(ReportChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    report_path = 'report'
    parent_field = 'report'
    queryset = ReportRevision.objects.all()
    serializer_class = ReportRevisionSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        import hashlib, json
        self._validate_related_scope(serializer)
        self._guard(serializer.validated_data['report'])
        content = serializer.validated_data.get("content", {})
        digest = hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()
        serializer.save(created_by=self.request.user, content_hash=digest)

class ChecklistAnswerViewSet(ReportChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    report_path = 'report_revision__report'
    parent_field = 'report_revision'
    queryset = ChecklistAnswer.objects.all()
    serializer_class = ChecklistAnswerSerializer
    permission_classes = [RoleAndScopePermission]

class MeasurementViewSet(ReportChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    report_path = 'report_revision__report'
    parent_field = 'report_revision'
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = [RoleAndScopePermission]

class AttachmentViewSet(ReportChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    report_path = 'report_revision__report'
    parent_field = 'report_revision'
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        self._validate_related_scope(serializer)
        self._guard(serializer.validated_data['report_revision'].report)
        upload = serializer.validated_data['file']
        serializer.save(
            uploaded_by=self.request.user,
            filename=upload.name[:255],
            file_size=upload.size,
            content_type=(getattr(upload, 'content_type', '') or '')[:128],
        )

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        attachment = self.get_object()
        return protected_file_response(attachment.file, attachment.filename)

class InstrumentViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [RoleAndScopePermission]

class InspectionTemplateViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = InspectionTemplate.objects.all()
    serializer_class = InspectionTemplateSerializer
    permission_classes = [RoleAndScopePermission]

class TemplateVersionViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = TemplateVersion.objects.all()
    serializer_class = TemplateVersionSerializer
    permission_classes = [RoleAndScopePermission]

class NCRViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'closed', 'waived'})
    queryset = NCR.objects.all()
    serializer_class = NCRSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        from apps.notifications.tasks import notify_ncr_creation
        notify_ncr_creation(serializer.instance)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        instance = self.get_object()
        if instance.status in ['closed', 'waived']:
            return Response({'detail': 'NCR is already closed or waived.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'closed'
        instance.closed_by = request.user
        instance.closed_at = timezone.now()
        instance.closure_notes = request.data.get('notes', '')
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        instance = self.get_object()
        if instance.status in ['closed', 'waived']:
            return Response({'detail': 'NCR is already closed or waived.'}, status=status.HTTP_400_BAD_REQUEST)
        if not str(request.data.get('reason', '')).strip():
            return Response({'reason': 'A justification is required to waive an NCR.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'waived'
        instance.closed_by = request.user
        instance.closed_at = timezone.now()
        instance.closure_notes = str(request.data.get('reason')).strip()
        instance.save()
        return Response(self.get_serializer(instance).data)

class CorrectiveActionViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer
    permission_classes = [RoleAndScopePermission]

class ReleaseNoteViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = ReleaseNote.objects.all()
    serializer_class = ReleaseNoteSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        self._validate_related_scope(serializer)
        serializer.save(released_by=self.request.user)
