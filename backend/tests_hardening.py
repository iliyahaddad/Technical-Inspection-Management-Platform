"""Regression tests for the hardening pass (auth, workflow locks, separation of duties, uploads, health)."""
import io

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.clients.models import Client
from apps.documents.validators import validate_upload
from apps.projects.models import Project

User = get_user_model()


def make_user(email, *roles, **extra):
    user = User.objects.create_user(email=email, password='Str0ng-pass-phrase!', **extra)
    for role in roles:
        user.groups.add(Group.objects.get_or_create(name=role)[0])
    return user


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_health_liveness_and_readiness(api):
    assert api.get('/api/health/').status_code == 200
    ready = api.get('/api/health/ready/')
    assert ready.status_code == 200 and ready.json()['checks']['database'] == 'ok'


@pytest.mark.django_db
def test_login_returns_tokens_and_logout_blacklists_refresh(api):
    make_user('a@example.com')
    res = api.post('/api/auth/token/', {'email': 'a@example.com', 'password': 'Str0ng-pass-phrase!'}, format='json')
    assert res.status_code == 200 and {'access', 'refresh'} <= set(res.json())
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {res.json()['access']}")
    assert api.post('/api/auth/logout/', {'refresh': res.json()['refresh']}, format='json').status_code == 204
    again = APIClient().post('/api/auth/token/refresh/', {'refresh': res.json()['refresh']}, format='json')
    assert again.status_code == 401


@pytest.mark.django_db
def test_me_exposes_roles_from_groups_not_from_client(api):
    user = make_user('c@example.com', 'coordinator')
    api.force_authenticate(user)
    body = api.get('/api/accounts/me/').json()
    assert body['roles'] == ['coordinator'] and body['is_staff'] is False
    # privilege fields are read-only through the API
    api.patch(f"/api/accounts/{user.pk}/", {'is_staff': True, 'is_active': False}, format='json')
    user.refresh_from_db()
    assert not user.is_staff and user.is_active


@pytest.mark.django_db
def test_request_review_accepts_both_payload_styles_and_requires_comment_for_reject(api):
    from apps.inspections.models import InspectionRequest
    coord = make_user('co@example.com', 'coordinator')
    client = Client.objects.create(client_code='C1', name='C1')
    project = Project.objects.create(client=client, project_code='P1', name='P1')
    irf = InspectionRequest.objects.create(project=project, submitted_by=coord, discipline='Mech', inspection_type='Final', status='submitted')
    api.force_authenticate(coord)
    assert api.post(f'/api/inspections/requests/{irf.pk}/review/', {'decision': 'reject'}, format='json').status_code == 400
    ok = api.post(f'/api/inspections/requests/{irf.pk}/review/', {'action': 'accepted'}, format='json')
    assert ok.status_code == 200 and ok.json()['status'] == 'accepted'
    # already reviewed -> cannot be reviewed twice
    assert api.post(f'/api/inspections/requests/{irf.pk}/review/', {'decision': 'accept'}, format='json').status_code == 400


@pytest.mark.django_db
def test_submitted_request_is_locked_for_generic_update(api):
    from apps.inspections.models import InspectionRequest
    coord = make_user('co2@example.com', 'coordinator')
    client = Client.objects.create(client_code='C2', name='C2')
    project = Project.objects.create(client=client, project_code='P2', name='P2')
    irf = InspectionRequest.objects.create(project=project, submitted_by=coord, discipline='Mech', inspection_type='Final', status='submitted')
    api.force_authenticate(coord)
    assert api.patch(f'/api/inspections/requests/{irf.pk}/', {'priority': 'urgent'}, format='json').status_code == 409


@pytest.mark.django_db
def test_audit_trail_records_actor_and_diff():
    from apps.audit.models import AuditEvent
    client = Client.objects.create(client_code='AUD', name='Before')
    client.name = 'After'
    client.save()
    events = list(AuditEvent.objects.filter(object_type='clients.Client', object_id=str(client.pk)).order_by('id'))
    assert [e.action for e in events] == ['create', 'update']
    assert events[1].changes['name'] == {'old': 'Before', 'new': 'After'}
    with pytest.raises(PermissionError):
        events[0].delete()


@pytest.mark.django_db
def test_audit_api_restricted_to_oversight_roles(api):
    api.force_authenticate(make_user('insp@example.com', 'inspector'))
    assert api.get('/api/audit/').status_code == 403
    api.force_authenticate(make_user('aud@example.com', 'auditor'))
    assert api.get('/api/audit/').status_code == 200


def _upload(name, content):
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(name, content)


def test_upload_validator_checks_magic_bytes():
    from django.core.exceptions import ValidationError
    validate_upload(_upload('ok.pdf', b'%PDF-1.7 rest'))
    with pytest.raises(ValidationError):
        validate_upload(_upload('evil.pdf', b'<html><script>alert(1)</script>'))
    with pytest.raises(ValidationError):
        validate_upload(_upload('run.exe', b'MZ\x90\x00'))


def test_pdf_generators_survive_markup_in_user_text():
    from apps.documents.pdf_generator import generate_inspection_report_pdf
    buf = generate_inspection_report_pdf({'report_number': 'R<b>1', 'narrative': '<script>&</script>', 'findings': [{'description': '<i>x', 'status': 'ok'}]})
    assert buf.getvalue().startswith(b'%PDF-')


# ---------------------------------------------------------------- v4 additions: 2FA, pagination, report locks
@pytest.mark.django_db
def test_page_size_query_param_is_honoured(api):
    for i in range(5):
        Client.objects.create(client_code=f'PG{i}', name=f'PG{i}')
    api.force_authenticate(make_user('gm@example.com', 'gm'))
    body = api.get('/api/clients/?page_size=2').json()
    assert body['count'] >= 5 and len(body['results']) == 2


@pytest.mark.django_db
def test_enrolled_user_must_supply_otp_at_login(api):
    from django_otp.plugins.otp_totp.models import TOTPDevice
    user = make_user('otp@example.com', 'coordinator')
    device = TOTPDevice.objects.create(user=user, name='primary', confirmed=True)
    creds = {'email': 'otp@example.com', 'password': 'Str0ng-pass-phrase!'}
    assert api.post('/api/auth/token/', creds, format='json').status_code == 401
    assert api.post('/api/auth/token/', {**creds, 'otp': '000000'}, format='json').status_code == 401
    from django_otp.oath import TOTP
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    totp.time = __import__('time').time()
    assert api.post('/api/auth/token/', {**creds, 'otp': str(totp.token()).zfill(device.digits)}, format='json').status_code == 200


@pytest.mark.django_db
def test_mandatory_2fa_blocks_api_until_enrolled_but_allows_enrolment(api, settings):
    settings.INTERNAL_2FA_REQUIRED = True
    user = make_user('gm2@example.com', 'gm')
    api.force_authenticate(user)
    assert api.get('/api/clients/').status_code == 403
    assert api.get('/api/accounts/me/').status_code == 200
    setup = api.post('/api/auth/2fa/setup/')
    assert setup.status_code == 200 and setup.json()['secret']
    assert api.post('/api/auth/2fa/disable/', {}, format='json').status_code == 403


@pytest.mark.django_db
def test_external_roles_are_not_forced_into_2fa(api, settings):
    settings.INTERNAL_2FA_REQUIRED = True
    api.force_authenticate(make_user('insp2@example.com', 'inspector'))
    assert api.post('/api/auth/2fa/setup/').status_code == 403


@pytest.mark.django_db
def test_report_attachments_locked_after_submit(api):
    from apps.reports.models import InspectionReport, ReportRevision
    from config.workflow import Conflict
    from apps.reports.views import ReportChildLockMixin
    owner = make_user('rep@example.com', 'inspector')
    report = InspectionReport(status='submitted')
    mixin = ReportChildLockMixin()
    with pytest.raises(Conflict):
        mixin._guard(report)
    mixin._guard(InspectionReport(status='draft'))  # draft stays editable


@pytest.mark.django_db
def test_metrics_endpoint_is_closed_by_default(client, settings):
    settings.DEBUG = False
    settings.METRICS_TOKEN = ''
    assert client.get('/metrics/').status_code == 403
