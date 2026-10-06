from django.apps import apps as django_apps
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.audit.middleware import get_current_request
from apps.audit.utils import _get_changes, log_audit, snapshot

_AUDIT_DISABLED = False


def disable_audit():
    global _AUDIT_DISABLED
    _AUDIT_DISABLED = True


def enable_audit():
    global _AUDIT_DISABLED
    _AUDIT_DISABLED = False


def _is_audited(sender):
    """Only business models in apps.* (never the audit app itself, sessions, token blacklist, celery-beat, ...)."""
    if _AUDIT_DISABLED:
        return False
    config = django_apps.get_containing_app_config(sender.__module__)
    return bool(config and config.name.startswith("apps.") and config.name != "apps.audit")


@receiver(pre_save)
def audit_pre_save(sender, instance, raw=False, **kwargs):
    if raw or not _is_audited(sender) or instance.pk is None:
        return
    instance._audit_old_instance = sender._default_manager.filter(pk=instance.pk).first()


@receiver(post_save)
def audit_post_save(sender, instance, created, raw=False, **kwargs):
    if raw or not _is_audited(sender):
        return
    request = get_current_request()
    if created:
        log_audit(request, instance, "create", snapshot(instance))
        return
    changes = _get_changes(getattr(instance, "_audit_old_instance", None), instance)
    instance._audit_old_instance = None
    if changes:
        log_audit(request, instance, "update", changes)


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not _is_audited(sender):
        return
    log_audit(get_current_request(), instance, "delete", snapshot(instance))
