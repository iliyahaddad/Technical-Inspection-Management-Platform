import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.clients.models import Client
from apps.projects.models import Project
from apps.inspections.models import InspectorProfile, Assignment, InspectionVisit
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
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def inspector_user(db):
    from conftest import grant
    return grant(User.objects.create_user(email='inspector@example.com', password='testpass123', first_name='Inspector', last_name='User'), 'inspector')

@pytest.fixture
def inspector_profile(db, inspector_user):
    return InspectorProfile.objects.create(user=inspector_user, employment_type='contractor', disciplines=['Mechanical'])

@pytest.fixture
def coordinator(db):
    from conftest import grant
    return grant(User.objects.create_user(email='coordinator@example.com', password='testpass123', first_name='Coordinator', last_name='User'), 'coordinator', 'finance_officer', 'quality_manager')

@pytest.fixture
def client_obj(db):
    return Client.objects.create(client_code='TEST-CLIENT', name='Test Client', contact_email='test@example.com')

@pytest.fixture
def project(db, client_obj):
    return Project.objects.create(client=client_obj, project_code='PRJ-001', name='Test Project', currency='IRR')

@pytest.fixture
def assignment(db, inspector_profile, project, coordinator):
    from apps.inspections.models import InspectionRequest, RequestItem, InspectionNotification
    req = InspectionRequest.objects.create(
        project=project,
        submitted_by=coordinator,
        discipline='Mechanical',
        inspection_type='Pre-Shipment',
        priority='normal',
        status='accepted',
    )
    RequestItem.objects.create(request=req, item_number=1, description='Valve', quantity=10, unit='pcs', previously_inspected_qty=0, requested_qty=10)
    notif = InspectionNotification.objects.create(
        inspection_request=req,
        project=project,
        inspection_date='2026-10-01T10:00:00Z',
        inspection_type='Pre-Shipment',
        notice_period_days=4,
        issued_by=coordinator,
        status='issued',
    )
    return Assignment.objects.create(
        notification=notif,
        inspector=inspector_profile,
        proposed_by=coordinator,
        status='accepted',
    )

@pytest.fixture
def visit(db, assignment):
    return InspectionVisit.objects.create(
        assignment=assignment,
        scheduled_start='2026-10-01T09:00:00Z',
        scheduled_end='2026-10-01T17:00:00Z',
        status='completed',
    )

class TestTimesheet:
    def test_create_timesheet(self, api_client, inspector_profile, project):
        api_client.force_authenticate(user=inspector_profile.user)
        payload = {
            'inspector': inspector_profile.id,
            'project': project.id,
            'month': '2026-10-01',
            'status': 'draft',
        }
        response = api_client.post('/api/mts/timesheets/', payload, format='json')
        assert response.status_code == 201
        assert Timesheet.objects.count() == 1

    def test_timesheet_workflow(self, api_client, inspector_profile, project, coordinator):
        api_client.force_authenticate(user=inspector_profile.user)
        payload = {
            'inspector': inspector_profile.id,
            'project': project.id,
            'month': '2026-10-01',
            'status': 'draft',
        }
        create_resp = api_client.post('/api/mts/timesheets/', payload, format='json')
        timesheet_id = create_resp.data['id']
        submit_resp = api_client.post(f'/api/mts/timesheets/{timesheet_id}/submit/')
        assert submit_resp.status_code == 200
        assert submit_resp.data['status'] == 'submitted'
        api_client.force_authenticate(user=coordinator)
        approve_resp = api_client.post(f'/api/mts/timesheets/{timesheet_id}/approve/')
        assert approve_resp.status_code == 200
        assert approve_resp.data['status'] == 'approved'
        lock_resp = api_client.post(f'/api/mts/timesheets/{timesheet_id}/lock/')
        assert lock_resp.status_code == 200
        assert lock_resp.data['status'] == 'locked'

class TestTimesheetEntry:
    def test_create_timesheet_entry(self, api_client, inspector_profile, project, visit):
        api_client.force_authenticate(user=inspector_profile.user)
        timesheet = Timesheet.objects.create(inspector=inspector_profile, project=project, month='2026-10-01')
        payload = {
            'timesheet': timesheet.id,
            'work_date': '2026-10-01',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'break_duration': 60,
            'actual_hours': 7.0,
            'travel_hours': 1.0,
            'waiting_hours': 0,
            'overtime_hours': 0,
            'location': 'Tehran',
            'description': 'Inspection work',
            'visit': visit.id,
        }
        response = api_client.post('/api/mts/timesheet-entries/', payload, format='json')
        assert response.status_code == 201
        assert TimesheetEntry.objects.count() == 1

class TestExpense:
    def test_expense_workflow(self, api_client, inspector_profile, project, coordinator):
        api_client.force_authenticate(user=inspector_profile.user)
        payload = {
            'inspector': inspector_profile.id,
            'project': project.id,
            'expense_date': '2026-10-01',
            'category': 'Travel',
            'amount': 500.00,
            'currency': 'IRR',
            'description': 'Flight to site',
            'status': 'draft',
        }
        create_resp = api_client.post('/api/mts/expenses/', payload, format='json')
        assert create_resp.status_code == 201
        expense_id = create_resp.data['id']
        submit_resp = api_client.post(f'/api/mts/expenses/{expense_id}/submit/')
        assert submit_resp.status_code == 200
        assert submit_resp.data['status'] == 'submitted'
        api_client.force_authenticate(user=coordinator)
        approve_resp = api_client.post(f'/api/mts/expenses/{expense_id}/approve/')
        assert approve_resp.status_code == 200
        assert approve_resp.data['status'] == 'approved'

class TestRateCard:
    def test_create_rate_card_with_revisions(self, api_client, coordinator, project):
        from apps.projects.models import Contract
        contract = Contract.objects.create(
            project=project,
            contract_number='CON-001',
            title='Test Contract',
            contract_type='person_day',
            total_value=100000,
            currency='IRR',
            start_date='2026-01-01',
            end_date='2026-12-31',
        )
        api_client.force_authenticate(user=coordinator)
        payload = {
            'contract': contract.id,
            'name': 'Mechanical Rates',
            'billing_model': 'person_day',
            'currency': 'IRR',
            'region': 'Tehran',
            'effective_date': '2026-01-01',
            'revisions': [
                {'revision_number': '1', 'rate_type': 'person_day', 'unit': 'day', 'amount': 1000, 'currency': 'IRR', 'effective_date': '2026-01-01'},
            ]
        }
        response = api_client.post('/api/mts/rate-cards/', payload, format='json')
        assert response.status_code == 201
        assert RateCard.objects.count() == 1
        assert RateRevision.objects.count() == 1

class TestCurrencyRate:
    def test_create_currency_rate(self, api_client, coordinator):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'from_currency': 'USD',
            'to_currency': 'IRR',
            'rate': 42000,
            'effective_date': '2026-10-01',
        }
        response = api_client.post('/api/mts/currency-rates/', payload, format='json')
        assert response.status_code == 201
        assert CurrencyRate.objects.count() == 1

class TestFinancialStatement:
    def test_create_statement_with_lines(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'currency': 'IRR',
            'total_billable': 500000,
            'total_invoiced': 300000,
            'current_amount': 200000,
            'lines': [
                {'line_type': 'timesheet', 'description': 'October timesheets', 'amount': 300000, 'currency': 'IRR'},
                {'line_type': 'expense', 'description': 'Travel expenses', 'amount': 50000, 'currency': 'IRR'},
            ]
        }
        response = api_client.post('/api/mts/statements/', payload, format='json')
        assert response.status_code == 201
        assert FinancialStatement.objects.count() == 1
        assert StatementLine.objects.count() == 2

    def test_statement_approve_and_lock(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'currency': 'IRR',
            'total_billable': 500000,
            'current_amount': 200000,
        }
        create_resp = api_client.post('/api/mts/statements/', payload, format='json')
        statement_id = create_resp.data['id']
        approve_resp = api_client.post(f'/api/mts/statements/{statement_id}/approve/')
        assert approve_resp.status_code == 200
        assert approve_resp.data['status'] == 'approved'
        lock_resp = api_client.post(f'/api/mts/statements/{statement_id}/lock/')
        assert lock_resp.status_code == 200
        assert lock_resp.data['status'] == 'sent'

class TestInvoiceAndPayment:
    def test_create_invoice_and_payment(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        stmt_payload = {
            'project': project.id,
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'currency': 'IRR',
            'total_billable': 500000,
            'current_amount': 200000,
        }
        stmt_resp = api_client.post('/api/mts/statements/', stmt_payload, format='json')
        statement_id = stmt_resp.data['id']
        invoice_payload = {
            'statement': statement_id,
            'invoice_number': 'INV-001',
            'invoice_date': '2026-11-01',
            'amount': 200000,
            'currency': 'IRR',
        }
        invoice_resp = api_client.post('/api/mts/invoice-references/', invoice_payload, format='json')
        assert invoice_resp.status_code == 201
        payment_payload = {
            'statement': statement_id,
            'payment_date': '2026-11-15',
            'amount': 100000,
            'currency': 'IRR',
            'reference': 'BANK-123',
        }
        payment_resp = api_client.post('/api/mts/payments/', payment_payload, format='json')
        assert payment_resp.status_code == 201

class TestSignatureAndApproval:
    def test_create_signature_record(self, api_client, inspector_profile, project):
        api_client.force_authenticate(user=inspector_profile.user)
        payload = {
            'user': inspector_profile.user.id,
            'document_type': 'report',
            'document_id': '1',
            'revision': 1,
            'image': 'data:image/png;base64,abc123',
            'content_hash': 'abc123def456',
        }
        response = api_client.post('/api/mts/signatures/', payload, format='json')
        assert response.status_code == 201
        assert SignatureRecord.objects.count() == 1

    def test_create_approval_record(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'user': coordinator.id,
            'object_type': 'InspectionRequest',
            'object_id': '1',
            'action': 'review',
            'comments': 'Approved',
        }
        response = api_client.post('/api/mts/approvals/', payload, format='json')
        assert response.status_code == 201
        assert ApprovalRecord.objects.count() == 1
