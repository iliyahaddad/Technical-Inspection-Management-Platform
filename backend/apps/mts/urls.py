from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.mts.views import (
    TimesheetViewSet,
    TimesheetEntryViewSet,
    ExpenseViewSet,
    RateCardViewSet,
    RateRevisionViewSet,
    CurrencyRateViewSet,
    FinancialStatementViewSet,
    StatementLineViewSet,
    InvoiceReferenceViewSet,
    PaymentRecordViewSet,
    SignatureRecordViewSet,
    ApprovalRecordViewSet,
    CostLedgerViewSet,
)

router = DefaultRouter()
router.register(r'timesheets', TimesheetViewSet, basename='timesheet')
router.register(r'timesheet-entries', TimesheetEntryViewSet, basename='timesheetentry')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'rate-cards', RateCardViewSet, basename='ratecard')
router.register(r'rate-revisions', RateRevisionViewSet, basename='raterevision')
router.register(r'currency-rates', CurrencyRateViewSet, basename='currencyrate')
router.register(r'statements', FinancialStatementViewSet, basename='financialstatement')
router.register(r'statement-lines', StatementLineViewSet, basename='statementline')
router.register(r'invoice-references', InvoiceReferenceViewSet, basename='invoicereference')
router.register(r'payments', PaymentRecordViewSet, basename='paymentrecord')
router.register(r'signatures', SignatureRecordViewSet, basename='signaturerecord')
router.register(r'approvals', ApprovalRecordViewSet, basename='approvalrecord')
router.register(r'cost-ledger', CostLedgerViewSet, basename='costledger')

urlpatterns = [
    path('', include(router.urls)),
]
