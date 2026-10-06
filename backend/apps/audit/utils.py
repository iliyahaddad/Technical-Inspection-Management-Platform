import logging

from django.db import transaction

from config.middleware import client_ip

logger = logging.getLogger("audit")

REDACT_MARKERS = ("password", "token", "secret", "signature_image")
MAX_VALUE_LEN = 500


def _get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")[:1000] if request else ""


def _get_request_user(request):
    user = getattr(request, "user", None) if request else None
    return user if getattr(user, "is_authenticated", False) else None


def _is_redacted(field_name):
    lowered = field_name.lower()
    return any(marker in lowered for marker in REDACT_MARKERS)


def snapshot(instance):
    """Flat {field: str(value)} snapshot of concrete fields with secrets redacted."""
    data = {}
    for field in instance._meta.concrete_fields:
        if _is_redacted(field.name):
            continue
        value = field.value_from_object(instance)
        data[field.attname] = str(value)[:MAX_VALUE_LEN] if value is not None else None
    return data


def _get_changes(old_instance, new_instance):
    new_data = snapshot(new_instance)
    if old_instance is None:
        return new_data
    old_data = snapshot(old_instance)
    return {
        key: {"old": old_data.get(key), "new": new_value}
        for key, new_value in new_data.items()
        if old_data.get(key) != new_value
    }


def log_audit(request, instance, action, changes=None):
    """Persist an AuditEvent. Never raises: a savepoint isolates DB errors from the caller's transaction."""
    try:
        from .models import AuditEvent

        with transaction.atomic():
            AuditEvent.objects.create(
                user=_get_request_user(request),
                action=action,
                object_type=instance._meta.label,
                object_id=str(instance.pk),
                object_repr=str(instance)[:255],
                changes=changes,
                ip_address=client_ip(request) if request else None,
                user_agent=_get_user_agent(request),
            )
    except Exception:
        logger.exception("failed to write audit event for %s", getattr(instance._meta, "label", instance))
