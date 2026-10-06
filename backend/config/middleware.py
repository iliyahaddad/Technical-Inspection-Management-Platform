"""Structured request logging for state-changing API calls.

Replaces the previous MiddlewareMixin subclass whose ``process_response`` accepted an extra
positional argument, which made *every* request fail with a TypeError.
"""
import json
import logging

logger = logging.getLogger("audit.request")

_MUTATING = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def client_ip(request):
    """Client IP. Honors X-Forwarded-For only when the deployment declares trusted proxies."""
    from django.conf import settings

    num_proxies = int(getattr(settings, "NUM_PROXIES", 0) or 0)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if num_proxies and forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if len(parts) >= num_proxies:
            return parts[-num_proxies]
    return request.META.get("REMOTE_ADDR")


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in _MUTATING:
            try:
                user = getattr(request, "user", None)
                logger.info(json.dumps({
                    "user_id": user.pk if getattr(user, "is_authenticated", False) else None,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "ip": client_ip(request),
                }, ensure_ascii=False))
            except Exception:  # logging must never break a response
                logger.exception("request audit logging failed")
        return response
