"""Report lifecycle: create -> edit -> submit -> return -> edit (new revision) -> resubmit -> tamper check."""
import pytest
from rest_framework.test import APIClient

from tests_hardening import make_user


@pytest.fixture
def visit(db):
    from apps.clients.models import Client
    from apps.inspections.models import Assignment, InspectionNotification, InspectionRequest, InspectionVisit, InspectorProfile
    from apps.projects.models import Project
    coord = make_user('flow-coord@example.com', 'coordinator')
    insp_user = make_user('flow-insp@example.com', 'inspector')
    client = Client.objects.create(client_code='FLOW', name='Flow')
    project = Project.objects.create(client=client, project_code='FLOWP', name='Flow project')
    irf = InspectionRequest.objects.create(project=project, submitted_by=coord, discipline='Mech', inspection_type='Final', status='accepted')
    note = InspectionNotification.objects.create(inspection_request=irf, issued_by=coord, status='issued')
    profile = InspectorProfile.objects.create(user=insp_user)
    assignment = Assignment.objects.create(notification=note, inspector=profile, proposed_by=coord, status='accepted')
    return InspectionVisit.objects.create(assignment=assignment, status='in_progress'), insp_user


@pytest.mark.django_db
def test_report_edit_return_resubmit_cycle(visit):
    v, insp = visit
    reviewer = make_user('flow-rev@example.com', 'reviewer', 'quality_manager')
    api = APIClient(); api.force_authenticate(insp)
    created = api.post('/api/reports/reports/', {'inspection_visit': v.pk, 'scope': 's', 'narrative': 'n'}, format='json')
    assert created.status_code == 201, created.content
    rid = created.json()['id']
    assert api.patch(f'/api/reports/reports/{rid}/', {'narrative': 'n2'}, format='json').status_code == 200
    assert api.post(f'/api/reports/reports/{rid}/submit/').status_code == 200
    assert api.patch(f'/api/reports/reports/{rid}/', {'narrative': 'x'}, format='json').status_code == 409   # locked
    assert api.post(f'/api/reports/reports/{rid}/approve/').status_code == 403                              # not own report

    rv = APIClient(); rv.force_authenticate(reviewer)
    assert rv.post(f'/api/reports/reports/{rid}/return_for_revision/', {'comments': 'fix'}, format='json').status_code == 200
    edited = api.patch(f'/api/reports/reports/{rid}/', {'narrative': 'n3'}, format='json').json()
    assert edited['status'] == 'draft' and edited['revision'] == 2 and edited['content_hash'] == ''
    assert api.post(f'/api/reports/reports/{rid}/submit/').status_code == 200
    assert rv.post(f'/api/reports/reports/{rid}/approve/').status_code == 200
