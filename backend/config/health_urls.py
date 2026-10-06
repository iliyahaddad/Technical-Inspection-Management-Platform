from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.urls import path


def liveness(request):
    return JsonResponse({"status": "ok"})


def readiness(request):
    checks = {}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    try:
        cache.set("health:ping", "1", 5)
        checks["cache"] = "ok" if cache.get("health:ping") == "1" else "error"
    except Exception:
        checks["cache"] = "error"
    healthy = all(v == "ok" for v in checks.values())
    return JsonResponse({"status": "ok" if healthy else "degraded", "checks": checks}, status=200 if healthy else 503)


urlpatterns = [
    path("", liveness),
    path("ready/", readiness),
]
