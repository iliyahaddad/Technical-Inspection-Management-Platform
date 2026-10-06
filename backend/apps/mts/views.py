from config.access_control import ScopedAccessMixin, RoleAndScopePermission
from config.workflow import LockedStatusMixin, ChildLockMixin, TransitionMixin, forbid_self_review
from apps.documents.responses import protected_file_response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.mts.models import (
    Timesheet,
    TimesheetEntry,
    Expense,
    RateCard,
    RateRevision,
    CurrencyRate,
    FinancialStatement,
    StatementLine,
    InvoiceReference,
    PaymentRecord,
    SignatureRecord,
    ApprovalRecord,
    CostLedger,
)
from apps.mts.serializers import (
    TimesheetSerializer,
    TimesheetEntrySerializer,
    ExpenseSerializer,
    RateCardSerializer,
    RateRevisionSerializer,
    CurrencyRateSerializer,
    FinancialStatementSerializer,
    StatementLineSerializer,
    InvoiceReferenceSerializer,
    PaymentRecordSerializer,
    SignatureRecordSerializer,
    ApprovalRecordSerializer,
    CostLedgerSerializer,
)

class TimesheetViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'submitted', 'approved', 'locked'})
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'draft':
            return Response({'detail': 'Only draft timesheets can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'submitted'
        instance.submitted_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'submitted':
            return Response({'detail': 'Only submitted timesheets can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        forbid_self_review(request, instance.inspector.user_id, 'timesheet')
        instance.status = 'approved'
        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'approved':
            return Response({'detail': 'Only approved timesheets can be locked.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'locked'
        instance.save()
        return Response(self.get_serializer(instance).data)

class TimesheetEntryViewSet(ChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    parent_field = 'timesheet'
    parent_locked_statuses = frozenset({'submitted', 'approved', 'locked'})
    queryset = TimesheetEntry.objects.all()
    serializer_class = TimesheetEntrySerializer
    permission_classes = [RoleAndScopePermission]

class ExpenseViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'submitted', 'approved', 'rejected'})
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'submitted':
            return Response({'detail': 'Only submitted expenses can be rejected.'}, status=status.HTTP_400_BAD_REQUEST)
        forbid_self_review(request, instance.inspector.user_id, 'expense')
        instance.status = 'rejected'
        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['get'], url_path='download-receipt')
    def download_receipt(self, request, pk=None):
        return protected_file_response(self.get_object().receipt)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'draft':
            return Response({'detail': 'Only draft expenses can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'submitted'
        instance.submitted_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'submitted':
            return Response({'detail': 'Only submitted expenses can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        forbid_self_review(request, instance.inspector.user_id, 'expense')
        instance.status = 'approved'
        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

class RateCardViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = RateCard.objects.all()
    serializer_class = RateCardSerializer
    permission_classes = [RoleAndScopePermission]

class RateRevisionViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = RateRevision.objects.all()
    serializer_class = RateRevisionSerializer
    permission_classes = [RoleAndScopePermission]

class CurrencyRateViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = CurrencyRate.objects.all()
    serializer_class = CurrencyRateSerializer
    permission_classes = [RoleAndScopePermission]

class FinancialStatementViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'approved', 'sent', 'paid', 'partial'})
    queryset = FinancialStatement.objects.all()
    serializer_class = FinancialStatementSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'draft':
            return Response({'detail': 'Only draft statements can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'approved'
        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'approved':
            return Response({'detail': 'Only approved statements can be locked.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'sent'
        instance.locked_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

class StatementLineViewSet(ChildLockMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    parent_field = 'statement'
    parent_locked_statuses = frozenset({'approved', 'sent', 'paid', 'partial'})
    queryset = StatementLine.objects.all()
    serializer_class = StatementLineSerializer
    permission_classes = [RoleAndScopePermission]

class InvoiceReferenceViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = InvoiceReference.objects.all()
    serializer_class = InvoiceReferenceSerializer
    permission_classes = [RoleAndScopePermission]

class PaymentRecordViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [RoleAndScopePermission]

class SignatureRecordViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = SignatureRecord.objects.all()
    serializer_class = SignatureRecordSerializer
    permission_classes = [RoleAndScopePermission]

class ApprovalRecordViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = ApprovalRecord.objects.all()
    serializer_class = ApprovalRecordSerializer
    permission_classes = [RoleAndScopePermission]

class CostLedgerViewSet(ScopedAccessMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CostLedger.objects.all()
    serializer_class = CostLedgerSerializer
    permission_classes = [RoleAndScopePermission]
    filterset_fields = ['project', 'source_type', 'cost_date']
    ordering_fields = ['cost_date', 'amount']
