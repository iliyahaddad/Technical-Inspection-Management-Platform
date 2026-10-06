import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.clients.models import Client
from apps.projects.models import Project, Vendor, Location
from apps.inspections.models import (
    InspectionRequest,
    RequestItem,
    InspectionNotification,
    Assignment,
    InspectionVisit,
    InspectorProfile,
)
from apps.reports.models import (
    InspectionReport,
    ReportRevision,
    ChecklistAnswer,
    Measurement,
    Attachment,
    Instrument,
    NCR,
    CorrectiveAction,
    ReleaseNote,
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
def reviewer_user(db):
    from conftest import grant
    return grant(User.objects.create_user(email='reviewer@example.com', password='testpass123', first_name='Reviewer', last_name='User'), 'reviewer', 'quality_manager')

@pytest.fixture
def client_obj(db):
    return Client.objects.create(client_code='TEST-CLIENT', name='Test Client', contact_email='test@example.com')

@pytest.fixture
def project(db, client_obj):
    return Project.objects.create(client=client_obj, project_code='PRJ-001', name='Test Project', currency='IRR')

@pytest.fixture
def vendor(db):
    return Vendor.objects.create(name='Test Vendor')

@pytest.fixture
def location(db):
    return Location.objects.create(name='Test Location', city='Tehran')

@pytest.fixture
def accepted_request(db, project, inspector_user):
    req = InspectionRequest.objects.create(
        project=project,
        submitted_by=inspector_user,
        discipline='Mechanical',
        inspection_type='Pre-Shipment',
        priority='normal',
        status='accepted',
    )
    RequestItem.objects.create(request=req, item_number=1, description='Valve', quantity=10, unit='pcs', previously_inspected_qty=0, requested_qty=10)
    return req

@pytest.fixture
def notification(db, accepted_request, project, vendor, location, inspector_user):
    return InspectionNotification.objects.create(
        inspection_request=accepted_request,
        project=project,
        vendor=vendor,
        location=location,
        inspection_date='2026-10-01T10:00:00Z',
        inspection_type='Pre-Shipment',
        notice_period_days=4,
        issued_by=inspector_user,
        status='issued',
    )

@pytest.fixture
def assignment(db, notification, inspector_profile, inspector_user):
    return Assignment.objects.create(
        notification=notification,
        inspector=inspector_profile,
        proposed_by=inspector_user,
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

class TestInspectionReport:
    def test_create_draft_report(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'submitted_by': inspector_user.id,
            'scope': 'Full inspection of valve',
            'inspected_qty': 10,
            'accepted_qty': 9,
            'rejected_qty': 1,
            'remaining_qty': 0,
            'content_hash': 'abc123',
        }
        response = api_client.post('/api/reports/reports/', payload, format='json')
        assert response.status_code == 201
        assert InspectionReport.objects.count() == 1
        assert InspectionReport.objects.first().status == 'draft'

    def test_report_submit_approve_issue_workflow(self, api_client, inspector_user, reviewer_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'submitted_by': inspector_user.id,
            'scope': 'Full inspection',
            'inspected_qty': 10,
            'accepted_qty': 10,
            'rejected_qty': 0,
            'remaining_qty': 0,
            'content_hash': 'abc123',
        }
        create_resp = api_client.post('/api/reports/reports/', payload, format='json')
        report_id = create_resp.data['id']
        submit_resp = api_client.post(f'/api/reports/reports/{report_id}/submit/')
        assert submit_resp.status_code == 200
        assert submit_resp.data['status'] == 'submitted'
        api_client.force_authenticate(user=reviewer_user)
        approve_resp = api_client.post(f'/api/reports/reports/{report_id}/approve/')
        assert approve_resp.status_code == 200
        assert approve_resp.data['status'] == 'approved'
        issue_resp = api_client.post(f'/api/reports/reports/{report_id}/issue/')
        assert issue_resp.status_code == 200
        assert issue_resp.data['status'] == 'issued'

class TestReportRevisions:
    def test_create_report_revision(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'submitted_by': inspector_user.id,
            'scope': 'Full inspection',
            'inspected_qty': 10,
            'accepted_qty': 10,
            'rejected_qty': 0,
            'remaining_qty': 0,
            'content_hash': 'abc123',
        }
        create_resp = api_client.post('/api/reports/reports/', payload, format='json')
        report_id = create_resp.data['id']
        rev_payload = {
            'report': report_id,
            'revision_number': 1,
            'content': {'scope': 'Full inspection'},
            'content_hash': 'def456',
            'created_by': inspector_user.id,
        }
        rev_resp = api_client.post('/api/reports/revisions/', rev_payload, format='json')
        assert rev_resp.status_code == 201
        assert ReportRevision.objects.count() == 1

class TestChecklistAndMeasurement:
    def test_add_checklist_answer(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'submitted_by': inspector_user.id,
            'scope': 'Full inspection',
            'inspected_qty': 10,
            'accepted_qty': 10,
            'rejected_qty': 0,
            'remaining_qty': 0,
            'content_hash': 'abc123',
        }
        create_resp = api_client.post('/api/reports/reports/', payload, format='json')
        report_id = create_resp.data['id']
        rev_payload = {
            'report': report_id,
            'revision_number': 1,
            'content': {'scope': 'Full inspection'},
            'content_hash': 'def456',
            'created_by': inspector_user.id,
        }
        rev_resp = api_client.post('/api/reports/revisions/', rev_payload, format='json')
        revision_id = rev_resp.data['id']
        checklist_payload = {
            'report_revision': revision_id,
            'activity_id': 'A1',
            'answer': 'pass',
            'remarks': 'OK',
        }
        checklist_resp = api_client.post('/api/reports/checklist-answers/', checklist_payload, format='json')
        assert checklist_resp.status_code == 201
        assert ChecklistAnswer.objects.count() == 1
        measurement_payload = {
            'report_revision': revision_id,
            'parameter': 'Diameter',
            'value': '100.5',
            'unit': 'mm',
            'tolerance': '±1.0',
            'result': 'pass',
        }
        measurement_resp = api_client.post('/api/reports/measurements/', measurement_payload, format='json')
        assert measurement_resp.status_code == 201
        assert Measurement.objects.count() == 1

class TestInstrument:
    def test_create_instrument(self, api_client, inspector_user):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'name': 'Calibrator',
            'serial_number': 'INST-001',
            'calibration_date': '2026-01-01',
            'expiry_date': '2027-01-01',
            'certificate_number': 'CERT-INST-001',
        }
        response = api_client.post('/api/reports/instruments/', payload, format='json')
        assert response.status_code == 201
        assert Instrument.objects.count() == 1

class TestNCR:
    def test_create_and_close_ncr(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'description': 'Surface defect found',
            'requirement_reference': 'ISO 9001',
            'severity': 'major',
            'responsible_party': inspector_user.id,
            'proposed_corrective_action': 'Rework',
            'target_completion_date': '2026-10-15',
        }
        response = api_client.post('/api/reports/ncrs/', payload, format='json')
        assert response.status_code == 201
        assert NCR.objects.count() == 1
        ncr_id = response.data['id']
        close_resp = api_client.post(f'/api/reports/ncrs/{ncr_id}/close/')
        assert close_resp.status_code == 200
        assert close_resp.data['status'] == 'closed'

    def test_waive_ncr(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'description': 'Minor deviation',
            'severity': 'minor',
        }
        response = api_client.post('/api/reports/ncrs/', payload, format='json')
        ncr_id = response.data['id']
        waive_resp = api_client.post(f'/api/reports/ncrs/{ncr_id}/waive/')
        assert waive_resp.status_code == 200
        assert waive_resp.data['status'] == 'waived'

class TestCorrectiveAction:
    def test_create_corrective_action(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        ncr_payload = {
            'inspection_visit': visit.id,
            'description': 'Defect',
            'severity': 'major',
        }
        ncr_resp = api_client.post('/api/reports/ncrs/', ncr_payload, format='json')
        ncr_id = ncr_resp.data['id']
        ca_payload = {
            'ncr': ncr_id,
            'description': 'Replace component',
            'assigned_to': inspector_user.id,
            'due_date': '2026-10-15',
        }
        ca_resp = api_client.post('/api/reports/corrective-actions/', ca_payload, format='json')
        assert ca_resp.status_code == 201
        assert CorrectiveAction.objects.count() == 1

class TestReleaseNote:
    def test_create_release_note(self, api_client, inspector_user, visit):
        api_client.force_authenticate(user=inspector_user)
        payload = {
            'inspection_visit': visit.id,
            'released_by': inspector_user.id,
            'notes': 'Hold point released',
            'is_final': True,
        }
        response = api_client.post('/api/reports/release-notes/', payload, format='json')
        assert response.status_code == 201
        assert ReleaseNote.objects.count() == 1
        assert ReleaseNote.objects.first().is_final is True
