import pytest


@pytest.mark.django_db
def test_metrics_forbidden_without_token(client, settings):
    settings.DEBUG = False
    settings.METRICS_TOKEN = 's3cret-token'
    assert client.get('/metrics/').status_code == 403
    assert client.get('/metrics/', HTTP_AUTHORIZATION='Bearer wrong').status_code == 403


@pytest.mark.django_db
def test_metrics_with_token_exposes_request_counter(client, settings):
    settings.DEBUG = False
    settings.METRICS_TOKEN = 's3cret-token'
    client.get('/api/health/')
    response = client.get('/metrics/', HTTP_AUTHORIZATION='Bearer s3cret-token')
    assert response.status_code == 200
    assert b'inspection_http_requests_total' in response.content
