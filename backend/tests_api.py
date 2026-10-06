import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.projects.models import Project

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_superuser(email='test@example.com', password='testpass123', first_name='Test', last_name='User')

@pytest.fixture
def client_user(db):
    user = User.objects.create_user(email='client@example.com', password='testpass123')
    client = Client.objects.create(client_code='TEST-CLIENT', name='Test Client')
    return {'user': user, 'client': client}

class TestAuthAPI:
    def test_login_missing_fields(self, api_client):
        response = api_client.post('/api/auth/token/', {})
        assert response.status_code == 400

    def test_register_user(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/accounts/')
        assert response.status_code == 200

class TestClientAPI:
    def test_list_clients(self, api_client, user):
        api_client.force_authenticate(user=user)
        Client.objects.create(client_code='CLIENT-A', name='Client A')
        response = api_client.get('/api/clients/')
        assert response.status_code == 200
        data = response.data
        if isinstance(data, dict):
            assert len(data.get('results', [])) == 1
        else:
            assert len(data) == 1

    def test_create_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.post('/api/clients/', {'client_code': 'NEW-CLIENT', 'name': 'New Client', 'contact_email': 'new@example.com'})
        assert response.status_code == 201
        assert Client.objects.count() == 1

class TestProjectAPI:
    def test_create_project(self, api_client, user, client_user):
        api_client.force_authenticate(user=user)
        response = api_client.post('/api/projects/projects/', {
            'client_id': client_user['client'].id,
            'project_code': 'PRJ-001',
            'name': 'Test Project',
            'currency': 'IRR',
        })
        assert response.status_code == 201
        assert Project.objects.count() == 1

@pytest.mark.django_db
def test_client_api_cannot_read_or_mutate_another_tenant_project(api_client):
    from django.contrib.auth.models import Group
    from apps.clients.models import ClientUser
    from apps.projects.models import Project
    user_a = User.objects.create_user(email='tenant-a@example.test', password='Safe-Test-Password-123')
    user_b = User.objects.create_user(email='tenant-b@example.test', password='Safe-Test-Password-123')
    role = Group.objects.create(name='client_requester')
    user_a.groups.add(role)
    user_b.groups.add(role)
    client_a = Client.objects.create(client_code='TENANT-A', name='Tenant A')
    client_b = Client.objects.create(client_code='TENANT-B', name='Tenant B')
    ClientUser.objects.create(user=user_a, client=client_a, role='requester')
    ClientUser.objects.create(user=user_b, client=client_b, role='requester')
    project_a = Project.objects.create(client=client_a, project_code='PROJECT-A', name='A')
    project_b = Project.objects.create(client=client_b, project_code='PROJECT-B', name='B')
    api_client.force_authenticate(user=user_a)
    response = api_client.get('/api/projects/projects/')
    assert response.status_code == 200
    rows = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
    assert {row['id'] for row in rows} == {project_a.pk}
    assert api_client.get(f'/api/projects/projects/{project_b.pk}/').status_code == 404
    assert api_client.patch(f'/api/projects/projects/{project_b.pk}/', {'name': 'stolen'}, format='json').status_code == 404
