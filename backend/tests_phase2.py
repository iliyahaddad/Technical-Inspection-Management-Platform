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
    ITP,
    ITPActivity,
    InspectorProfile,
    Certificate,
    Availability,
    Assignment,
    InspectionVisit,
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def coordinator(db):
    from conftest import grant
    return grant(User.objects.create_user(email='coordinator@example.com', password='testpass123', first_name='Coordinator', last_name='User'), 'coordinator', 'finance_officer', 'quality_manager')

@pytest.fixture
def inspector_user(db):
    from conftest import grant
    return grant(User.objects.create_user(email='inspector@example.com', password='testpass123', first_name='Inspector', last_name='User'), 'inspector')

@pytest.fixture
def inspector_profile(db, inspector_user):
    return InspectorProfile.objects.create(user=inspector_user, employment_type='contractor', disciplines=['Mechanical'])

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
def accepted_request(db, project, coordinator):
    req = InspectionRequest.objects.create(
        project=project,
        submitted_by=coordinator,
        discipline='Mechanical',
        inspection_type='Pre-Shipment',
        priority='normal',
        status='accepted',
    )
    RequestItem.objects.create(request=req, item_number=1, description='Valve', quantity=10, unit='pcs', previously_inspected_qty=0, requested_qty=10)
    return req

@pytest.fixture
def itp(db, project):
    return ITP.objects.create(project=project, itp_number='ITP-001', title='Mechanical ITP')

@pytest.fixture
def itp_activity(db, itp):
    return ITPActivity.objects.create(itp=itp, activity_number='A1', description='Visual inspection', intervention_type='H')

class TestInspectionNotification:
    def test_create_notification(self, api_client, coordinator, accepted_request, project, vendor, location):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'inspection_request': accepted_request.id,
            'project': project.id,
            'vendor': vendor.id,
            'location': location.id,
            'inspection_date': '2026-10-01T10:00:00Z',
            'inspection_type': 'Pre-Shipment',
            'notice_period_days': 4,
            'issued_by': coordinator.id,
        }
        response = api_client.post('/api/inspections/notifications/', payload, format='json')
        assert response.status_code == 201
        assert InspectionNotification.objects.count() == 1
        assert InspectionNotification.objects.first().status == 'draft'

    def test_issue_and_acknowledge(self, api_client, coordinator, accepted_request, project, vendor, location):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'inspection_request': accepted_request.id,
            'project': project.id,
            'vendor': vendor.id,
            'location': location.id,
            'inspection_date': '2026-10-01T10:00:00Z',
            'inspection_type': 'Pre-Shipment',
            'notice_period_days': 4,
            'issued_by': coordinator.id,
        }
        create_resp = api_client.post('/api/inspections/notifications/', payload, format='json')
        notification_id = create_resp.data['id']
        issue_resp = api_client.post(f'/api/inspections/notifications/{notification_id}/issue/')
        assert issue_resp.status_code == 200
        assert issue_resp.data['status'] == 'issued'
        ack_resp = api_client.post(f'/api/inspections/notifications/{notification_id}/acknowledge/')
        assert ack_resp.status_code == 200
        assert ack_resp.data['status'] == 'acknowledged'

class TestITP:
    def test_create_itp_with_activities(self, api_client, coordinator, project, itp):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'itp_number': 'ITP-002',
            'title': 'New ITP',
            'revision': 'B',
            'applicable_standard': 'API 6D',
            'activities': [
                {'activity_number': 'A1', 'description': 'Visual', 'intervention_type': 'H', 'is_mandatory': True},
                {'activity_number': 'A2', 'description': 'NDT', 'intervention_type': 'W', 'is_mandatory': False},
            ]
        }
        response = api_client.post('/api/inspections/itps/', payload, format='json')
        assert response.status_code == 201
        assert ITP.objects.count() == 2
        assert ITPActivity.objects.count() == 2

class TestInspectorManagement:
    def test_create_inspector_profile(self, api_client, coordinator, inspector_user):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'user_id': inspector_user.id,
            'employment_type': 'contractor',
            'disciplines': ['Mechanical', 'NDT'],
            'geographic_location': 'Tehran',
        }
        response = api_client.post('/api/inspections/inspectors/', payload, format='json')
        assert response.status_code == 201
        assert InspectorProfile.objects.count() == 1

    def test_add_certificate(self, api_client, coordinator, inspector_profile):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'inspector': inspector_profile.id,
            'name': 'NDT Level 2',
            'issuing_body': 'PCN',
            'issue_date': '2024-01-01',
            'expiry_date': '2026-01-01',
            'certificate_number': 'CERT-001',
        }
        response = api_client.post('/api/inspections/certificates/', payload, format='json')
        assert response.status_code == 201
        assert Certificate.objects.count() == 1

    def test_set_availability(self, api_client, coordinator, inspector_profile):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'inspector': inspector_profile.id,
            'date': '2026-10-01',
            'is_available': True,
            'note': 'Available for assignment',
        }
        response = api_client.post('/api/inspections/availabilities/', payload, format='json')
        assert response.status_code == 201
        assert Availability.objects.count() == 1

class TestAssignmentWorkflow:
    def test_full_assignment_lifecycle(self, api_client, coordinator, inspector_profile, accepted_request, project, vendor, location, itp):
        api_client.force_authenticate(user=coordinator)
        notif_payload = {
            'inspection_request': accepted_request.id,
            'project': project.id,
            'vendor': vendor.id,
            'location': location.id,
            'inspection_date': '2026-10-01T10:00:00Z',
            'inspection_type': 'Pre-Shipment',
            'notice_period_days': 4,
            'issued_by': coordinator.id,
        }
        notif_resp = api_client.post('/api/inspections/notifications/', notif_payload, format='json')
        notification_id = notif_resp.data['id']
        api_client.post(f'/api/inspections/notifications/{notification_id}/issue/')
        api_client.post(f'/api/inspections/notifications/{notification_id}/acknowledge/')
        assign_payload = {
            'notification': notification_id,
            'inspector': inspector_profile.id,
            'proposed_by': coordinator.id,
        }
        assign_resp = api_client.post('/api/inspections/assignments/', assign_payload, format='json')
        assert assign_resp.status_code == 201
        assignment_id = assign_resp.data['id']
        api_client.post(f'/api/inspections/assignments/{assignment_id}/propose/')
        api_client.post(f'/api/inspections/assignments/{assignment_id}/notify/')
        api_client.post(f'/api/inspections/assignments/{assignment_id}/accept/')
        assert Assignment.objects.get(id=assignment_id).status == 'accepted'

class TestInspectionVisit:
    def test_visit_lifecycle(self, api_client, coordinator, inspector_profile, accepted_request, project, vendor, location, itp):
        api_client.force_authenticate(user=coordinator)
        notif_payload = {
            'inspection_request': accepted_request.id,
            'project': project.id,
            'vendor': vendor.id,
            'location': location.id,
            'inspection_date': '2026-10-01T10:00:00Z',
            'inspection_type': 'Pre-Shipment',
            'notice_period_days': 4,
            'issued_by': coordinator.id,
        }
        notif_resp = api_client.post('/api/inspections/notifications/', notif_payload, format='json')
        notification_id = notif_resp.data['id']
        assign_payload = {
            'notification': notification_id,
            'inspector': inspector_profile.id,
            'proposed_by': coordinator.id,
        }
        assign_resp = api_client.post('/api/inspections/assignments/', assign_payload, format='json')
        assignment_id = assign_resp.data['id']
        api_client.post(f'/api/inspections/assignments/{assignment_id}/propose/')
        api_client.post(f'/api/inspections/assignments/{assignment_id}/notify/')
        api_client.post(f'/api/inspections/assignments/{assignment_id}/accept/')
        visit_payload = {
            'assignment': assignment_id,
            'scheduled_start': '2026-10-01T09:00:00Z',
            'scheduled_end': '2026-10-01T17:00:00Z',
            'status': 'scheduled',
        }
        visit_resp = api_client.post('/api/inspections/visits/', visit_payload, format='json')
        assert visit_resp.status_code == 201
        visit_id = visit_resp.data['id']
        api_client.post(f'/api/inspections/visits/{visit_id}/start/')
        api_client.post(f'/api/inspections/visits/{visit_id}/complete/')
        assert InspectionVisit.objects.get(id=visit_id).status == 'completed'
