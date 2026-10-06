import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.clients.models import Client, ClientUser
from django.contrib.auth.models import Group
from apps.projects.models import Project
from apps.inspections.models import InspectionRequest, RequestItem

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def coordinator(db):
    user = User.objects.create_user(email='coordinator@example.com', password='testpass123', first_name='Coordinator', last_name='User')
    user.groups.add(Group.objects.create(name='coordinator'))
    return user

@pytest.fixture
def client_requester(db):
    user = User.objects.create_user(email='requester@example.com', password='testpass123', first_name='Requester', last_name='User')
    user.groups.add(Group.objects.create(name='client_requester'))
    return user

@pytest.fixture
def client_obj(db):
    return Client.objects.create(client_code='TEST-CLIENT', name='Test Client', contact_email='test@example.com')

@pytest.fixture
def project(db, client_obj, client_requester, coordinator):
    ClientUser.objects.create(user=client_requester, client=client_obj, role='requester')
    return Project.objects.create(client=client_obj, project_code='PRJ-001', name='Test Project', project_manager=coordinator, currency='IRR')

class TestInspectionRequestWorkflow:
    def test_create_draft_request(self, api_client, client_requester, project):
        api_client.force_authenticate(user=client_requester)
        payload = {
            'project': project.id,
            'submitted_by': client_requester.id,
            'discipline': 'Mechanical',
            'inspection_type': 'Pre-Shipment',
            'priority': 'normal',
            'status': 'draft',
            'items': [
                {'item_number': 1, 'description': 'Valve', 'quantity': 10, 'unit': 'pcs', 'previously_inspected_qty': 0, 'requested_qty': 10}
            ]
        }
        response = api_client.post('/api/inspections/requests/', payload, format='json')
        print(f"Create response: {response.status_code} {response.data}")
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.data}"
        assert InspectionRequest.objects.count() == 1
        assert InspectionRequest.objects.first().status == 'draft'

    def test_submit_request(self, api_client, client_requester, project):
        api_client.force_authenticate(user=client_requester)
        payload = {
            'project': project.id,
            'submitted_by': client_requester.id,
            'discipline': 'Mechanical',
            'inspection_type': 'Pre-Shipment',
            'priority': 'normal',
            'status': 'draft',
            'items': [
                {'item_number': 1, 'description': 'Valve', 'quantity': 10, 'unit': 'pcs', 'previously_inspected_qty': 0, 'requested_qty': 10}
            ]
        }
        create_resp = api_client.post('/api/inspections/requests/', payload, format='json')
        print(f"Create response: {create_resp.status_code} {create_resp.data}")
        request_id = create_resp.data['id']
        submit_resp = api_client.post(f'/api/inspections/requests/{request_id}/submit/')
        assert submit_resp.status_code == 200
        assert submit_resp.data['status'] == 'submitted'

    def test_coordinator_review_accept(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'submitted_by': coordinator.id,
            'discipline': 'Mechanical',
            'inspection_type': 'Pre-Shipment',
            'priority': 'normal',
            'status': 'submitted',
            'items': [
                {'item_number': 1, 'description': 'Valve', 'quantity': 10, 'unit': 'pcs', 'previously_inspected_qty': 0, 'requested_qty': 10}
            ]
        }
        create_resp = api_client.post('/api/inspections/requests/', payload, format='json')
        request_id = create_resp.data['id']
        review_resp = api_client.post(f'/api/inspections/requests/{request_id}/review/', {'decision': 'accept', 'comments': 'Looks good'})
        assert review_resp.status_code == 200
        assert review_resp.data['status'] == 'accepted'
        assert review_resp.data['review_comments'] == 'Looks good'

    def test_coordinator_review_reject(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'submitted_by': coordinator.id,
            'discipline': 'Mechanical',
            'inspection_type': 'Pre-Shipment',
            'priority': 'normal',
            'status': 'submitted',
            'items': [
                {'item_number': 1, 'description': 'Valve', 'quantity': 10, 'unit': 'pcs', 'previously_inspected_qty': 0, 'requested_qty': 10}
            ]
        }
        create_resp = api_client.post('/api/inspections/requests/', payload, format='json')
        request_id = create_resp.data['id']
        review_resp = api_client.post(f'/api/inspections/requests/{request_id}/review/', {'decision': 'reject', 'comments': 'Missing docs'})
        assert review_resp.status_code == 200
        assert review_resp.data['status'] == 'rejected'
        assert review_resp.data['review_comments'] == 'Missing docs'

    def test_coordinator_review_clarification(self, api_client, coordinator, project):
        api_client.force_authenticate(user=coordinator)
        payload = {
            'project': project.id,
            'submitted_by': coordinator.id,
            'discipline': 'Mechanical',
            'inspection_type': 'Pre-Shipment',
            'priority': 'normal',
            'status': 'submitted',
            'items': [
                {'item_number': 1, 'description': 'Valve', 'quantity': 10, 'unit': 'pcs', 'previously_inspected_qty': 0, 'requested_qty': 10}
            ]
        }
        create_resp = api_client.post('/api/inspections/requests/', payload, format='json')
        request_id = create_resp.data['id']
        review_resp = api_client.post(f'/api/inspections/requests/{request_id}/review/', {'decision': 'clarification', 'comments': 'Need more details'})
        assert review_resp.status_code == 200
        assert review_resp.data['status'] == 'clarification_required'
