"""Prometheus metrics: real per-request counters/latency, protected by a bearer token.

* ``/metrics/`` requires ``Authorization: Bearer <METRICS_TOKEN>``; with no token configured it is only
  reachable when DEBUG is on (so a forgotten setting never exposes metrics publicly).
* Under gunicorn each worker has its own registry. Set ``PROMETHEUS_MULTIPROC_DIR`` (a writable, empty-at-boot
  directory) to aggregate across workers.
"""
import hmac
import os
import time

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, Counter, Histogram, generate_latest, multiprocess

REQUESTS = Counter('inspection_http_requests_total', 'HTTP requests', ['method', 'route', 'status'])
LATENCY = Histogram('inspection_http_request_seconds', 'HTTP request latency', ['method', 'route'],
                    buckets=(0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10))


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)
        match = getattr(request, 'resolver_match', None)
        route = (match.route if match and match.route else 'unmatched')[:100]  # route template: bounded cardinality
        REQUESTS.labels(request.method, route, str(response.status_code)).inc()
        LATENCY.labels(request.method, route).observe(time.perf_counter() - started)
        return response


def metrics(request):
    token = getattr(settings, 'METRICS_TOKEN', '')
    if token:
        supplied = request.META.get('HTTP_AUTHORIZATION', '').removeprefix('Bearer ').strip()
        if not hmac.compare_digest(supplied.encode(), token.encode()):
            return HttpResponseForbidden('forbidden')
    elif not settings.DEBUG:
        return HttpResponseForbidden('metrics disabled: set METRICS_TOKEN')
    if os.environ.get('PROMETHEUS_MULTIPROC_DIR'):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = REGISTRY
    return HttpResponse(generate_latest(registry), content_type=CONTENT_TYPE_LATEST)
