import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.projects.models import Project, Contract

User = get_user_model()

class ClientModelTest(TestCase):
    def test_create_client(self):
        client = Client.objects.create(client_code='TEST-CLIENT', name='Test Client', contact_email='test@example.com')
        self.assertIn('Test Client', str(client))
        self.assertEqual(client.client_code, 'TEST-CLIENT')
        self.assertTrue(client.is_active)

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='pm@example.com', password='testpass123')
        self.client = Client.objects.create(client_code='CLIENT-A', name='Client A')

    def test_create_project(self):
        project = Project.objects.create(
            client=self.client,
            project_code='PRJ-001',
            name='Test Project',
            project_manager=self.user,
        )
        self.assertEqual(project.project_code, 'PRJ-001')
        self.assertEqual(project.status, 'draft')

class ContractModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='pm@example.com', password='testpass123')
        self.client = Client.objects.create(client_code='CLIENT-A', name='Client A')
        self.project = Project.objects.create(client=self.client, project_code='PRJ-001', name='Test Project')

    def test_create_contract(self):
        contract = Contract.objects.create(
            project=self.project,
            contract_number='CON-001',
            title='Test Contract',
            contract_type='person_day',
            total_value=100000,
            currency='IRR',
            start_date='2026-01-01',
            end_date='2026-12-31',
        )
        self.assertEqual(contract.contract_number, 'CON-001')
        self.assertEqual(contract.contract_type, 'person_day')
