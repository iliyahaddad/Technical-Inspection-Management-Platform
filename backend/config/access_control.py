from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS

INTERNAL_WIDE_ROLES = {
    "sys_admin", "gm", "tech_manager", "quality_manager", "coordinator",
    "reviewer", "finance_officer", "auditor",
}
CLIENT_ROLES = {"client_admin", "client_requester", "client_approver"}
INTERNAL_2FA_ROLES = INTERNAL_WIDE_ROLES | {"sys_admin", "project_manager"}
KNOWN_ROLES = INTERNAL_WIDE_ROLES | CLIENT_ROLES | {"project_manager", "inspector", "vendor_rep"}
FINANCE_APPS = {"apps.mts"}
INSPECTION_WRITE_APPS = {"apps.inspections"}
QUALITY_WRITE_APPS = {"apps.reports"}


def user_roles(user):
    if not user or not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True)) & KNOWN_ROLES


def needs_2fa(user):
    from django.conf import settings
    if not getattr(settings, "INTERNAL_2FA_REQUIRED", False) or not user or not user.is_authenticated:
        return False
    return bool(user.is_staff or user.is_superuser or user_roles(user) & INTERNAL_2FA_ROLES)


def has_confirmed_totp(user):
    from django_otp.plugins.otp_totp.models import TOTPDevice
    return TOTPDevice.objects.filter(user=user, confirmed=True).exists()


def is_global_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff or "sys_admin" in user_roles(user)))


def _client_ids(user):
    return list(user.client_links.values_list("client_id", flat=True))


def _managed_project_ids(user):
    from apps.projects.models import Project
    return Project.objects.filter(project_manager=user).values_list("pk", flat=True)


def _assigned_notification_ids(user):
    from apps.inspections.models import Assignment
    return Assignment.objects.filter(inspector__user=user).values_list("notification_id", flat=True)


def scoped_queryset(user, queryset):
    if is_global_admin(user):
        return queryset
    roles = user_roles(user)
    if not roles:
        return queryset.none()
    model = queryset.model
    label = model._meta.label_lower
    if label in {"documents.document", "documents.documentversion"}:
        return queryset.none()
    if label == "notifications.notification":
        return queryset.filter(user=user)
    if label in {"mts.signaturerecord", "mts.approvalrecord"}:
        return queryset.filter(user=user)
    if label == "audit.auditevent":
        return queryset if ("auditor" in roles or "gm" in roles or "quality_manager" in roles) else queryset.none()
    if roles & INTERNAL_WIDE_ROLES:
        return queryset
    projects = _managed_project_ids(user) if "project_manager" in roles else []
    clients = _client_ids(user) if roles & CLIENT_ROLES else []
    if projects:
        from apps.projects.models import Project
        clients = list(set(clients) | set(Project.objects.filter(pk__in=projects).values_list("client_id", flat=True)))
    inspector = "inspector" in roles

    if label == "clients.client":
        return queryset.filter(pk__in=clients) if clients else queryset.none()
    if label == "clients.clientuser":
        q = Q(user=user)
        if clients:
            q |= Q(client_id__in=clients)
        return queryset.filter(q)
    if label == "projects.project":
        q = Q(pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(client_id__in=clients)
        if "vendor_rep" in roles:
            vendor_ids = user.vendor_links.filter(is_active=True).values_list("vendor_id", flat=True)
            q |= Q(pk__in=projects) if projects else Q()
        return queryset.filter(q)
    if label == "projects.vendor":
        if "vendor_rep" in roles:
            vendor_ids = user.vendor_links.filter(is_active=True).values_list("vendor_id", flat=True)
            return queryset.filter(pk__in=vendor_ids)
        return queryset.none()
    if label == "projects.contract":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        return queryset.filter(q)
    if label == "projects.purchaseorder":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        return queryset.filter(q)
    if label == "projects.location":
        return queryset if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles else queryset.none()
    if label == "inspections.inspectionrequest":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        if inspector:
            q |= Q(pk__in=_assigned_notification_ids(user))
        return queryset.filter(q)
    if label == "inspections.inspectionnotification":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        if inspector:
            q |= Q(pk__in=_assigned_notification_ids(user))
        return queryset.filter(q)
    if label == "inspections.assignment":
        return queryset.filter(inspector__user=user) if inspector else queryset.none()
    if label == "inspections.inspectionvisit":
        q = Q(assignment__inspector__user=user) if inspector else Q(pk__in=[])
        if projects:
            q |= Q(assignment__notification__project__pk__in=projects)
        return queryset.filter(q)
    if label == "inspections.itp":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        return queryset.filter(q)
    if label == "inspections.inspectorprofile":
        if inspector:
            return queryset.filter(user=user)
        if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles:
            return queryset
        return queryset.none()
    if label == "inspections.certificate":
        if inspector:
            return queryset.filter(inspector__user=user)
        if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles:
            return queryset
        return queryset.none()
    if label == "inspections.availability":
        if inspector:
            return queryset.filter(inspector__user=user)
        if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles:
            return queryset
        return queryset.none()
    if label == "reports.inspectionreport":
        q = Q(inspection_visit__assignment__notification__project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(inspection_visit__assignment__notification__project__client_id__in=clients)
        if inspector:
            q |= Q(submitted_by=user)
        return queryset.filter(q)
    if label == "reports.ncr":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        return queryset.filter(q)
    if label == "reports.correctiveaction":
        q = Q(ncr__project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(ncr__project__client_id__in=clients)
        return queryset.filter(q)
    if label == "reports.releasenote":
        q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
        if clients:
            q |= Q(project__client_id__in=clients)
        return queryset.filter(q)
    if label == "reports.inspectiontemplate":
        return queryset if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles else queryset.none()
    if label == "reports.instrument":
        return queryset if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles else queryset.none()
    if label == "mts.timesheet":
        if inspector:
            return queryset.filter(inspector__user=user)
        if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles or "finance_officer" in roles:
            q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
            if clients:
                q |= Q(project__client_id__in=clients)
            return queryset.filter(q)
        return queryset.none()
    if label == "mts.expense":
        if inspector:
            return queryset.filter(inspector__user=user)
        if roles & INTERNAL_WIDE_ROLES or "project_manager" in roles or "finance_officer" in roles:
            q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
            if clients:
                q |= Q(project__client_id__in=clients)
            return queryset.filter(q)
        return queryset.none()
    if label == "mts.financialstatement":
        if roles & INTERNAL_WIDE_ROLES or "finance_officer" in roles or "gm" in roles:
            q = Q(project__pk__in=projects) if projects else Q(pk__in=[])
            if clients:
                q |= Q(project__client_id__in=clients)
            return queryset.filter(q)
        return queryset.none()
    if label == "notifications.notification":
        return queryset.filter(user=user)
    return queryset.none()


class RoleAndScopePermission(BasePermission):
    message = "Your role does not permit this operation or resource is outside your tenant scope."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if needs_2fa(user) and not has_confirmed_totp(user):
            self.message = "Two-factor authentication must be set up before using the platform."
            return False
        if is_global_admin(user):
            return True
        roles = user_roles(user)
        if not roles:
            return getattr(view, "basename", "") == "account" or getattr(view, "action", "") in {"me", "change_password"}
        action = getattr(view, "action", "")
        model = getattr(getattr(view, "queryset", None), "model", None)
        app = model._meta.app_label if model else ""
        name = model.__name__.lower() if model else ""
        if not model:
            label = getattr(view, "permission_model_label", "")
            if label:
                app, _, name = label.partition(".")
        if app == "audit":
            return request.method in SAFE_METHODS and bool(roles & {"auditor", "gm", "quality_manager"})
        if request.method in SAFE_METHODS or action in {"list", "retrieve", "metadata", "options", "head"}:
            if "auditor" in roles:
                return True
            if roles & CLIENT_ROLES:
                return app in {"clients", "projects", "inspections", "reports", "documents"}
            if "inspector" in roles:
                return (app == "inspections" and name in {"inspectorprofile", "certificate", "availability", "assignment", "inspectionvisit", "inspectionrequest", "inspectionnotification"}) or (app == "reports" and name in {"inspectionreport", "reportrevision", "checklistanswer", "measurement", "attachment", "ncr", "correctiveaction", "releasenote"}) or (app == "mts" and name in {"timesheet", "timesheetentry", "expense"}) or (app == "notifications" and name == "notification")
            if "finance_officer" in roles:
                return app in {"projects", "clients", "mts"} and name not in {"document", "documentversion"}
            if "project_manager" in roles:
                return app in {"projects", "clients", "inspections", "reports", "mts", "documents"}
            if roles & {"quality_manager", "reviewer"}:
                return app in {"projects", "clients", "inspections", "reports", "documents"} and name not in {"document", "documentversion"}
            if roles & {"coordinator", "tech_manager"}:
                return app in {"projects", "clients", "inspections", "reports"}
            if "gm" in roles:
                return app in {"clients", "projects", "inspections", "reports", "documents", "mts", "audit"}
            if "vendor_rep" in roles:
                return (app == "projects" and name in {"vendor", "vendoruser", "project", "purchaseorder"}) or (app == "documents" and name in {"document", "documentversion"})
            return False
        allowed = False
        if roles & CLIENT_ROLES:
            if app == "inspections" and name == "inspectionrequest":
                allowed = action in {"create", "update", "partial_update", "submit"} and bool(roles & {"client_admin", "client_requester"})
            elif app == "documents" and name == "document":
                allowed = action in {"create", "new_version"} and bool(roles & {"client_admin", "client_requester"})
        if not allowed and "inspector" in roles:
            if app == "reports" and name in {"inspectionreport", "reportrevision", "checklistanswer", "measurement", "attachment", "instrument", "ncr", "correctiveaction"} and action in {"create", "update", "partial_update", "submit"}:
                allowed = True
            elif app == "mts" and name in {"timesheet", "timesheetentry", "expense"} and action in {"create", "update", "partial_update", "submit"}:
                allowed = True
            elif app == "inspections" and name == "availability" and action in {"create", "update", "partial_update", "destroy"}:
                allowed = True
            elif app == "inspections" and name in {"inspectionvisit", "assignment"} and action in {"accept", "decline", "start", "complete", "update", "partial_update"}:
                allowed = True
        if not allowed and "finance_officer" in roles:
            if app == "mts" and name in {"timesheet", "timesheetentry", "expense", "ratecard", "raterevision", "currencyrate", "financialstatement", "statementline", "invoicereference", "paymentrecord", "costledger", "signaturerecord", "approvalrecord"}:
                allowed = True
        if not allowed and "project_manager" in roles:
            if app in {"projects", "inspections", "reports", "documents", "mts"} and name not in {"document", "documentversion"}:
                allowed = True
            if app == "projects" and name == "project" and action == "create":
                allowed = False
        if not allowed and roles & {"quality_manager", "reviewer"}:
            if app in {"inspections", "reports", "documents"}:
                allowed = True
        if not allowed and roles & {"coordinator", "tech_manager"}:
            if app in {"projects", "inspections", "reports", "documents"}:
                allowed = True
        if not allowed and "gm" in roles:
            if app in {"clients", "projects", "inspections", "reports", "documents", "mts"}:
                allowed = True
        if not allowed and "vendor_rep" in roles:
            if (app == "projects" and name in {"vendor", "vendoruser", "project", "purchaseorder"}) or (app == "documents" and name in {"document", "documentversion"} and action in {"create", "new_version"}):
                allowed = True
        if not allowed:
            return False
        if action in {"approve", "reject", "return_for_revision", "close", "waive"}:
            if app == "reports" and not roles & {"quality_manager", "reviewer", "gm"}:
                return False
            if app == "mts" and not roles & {"finance_officer", "gm"}:
                return False
            if action in {"close", "waive"} and not roles & {"quality_manager", "gm"}:
                return False
        if action == "issue" and app == "reports" and not roles & {"quality_manager", "reviewer", "gm"}:
            return False
        if action == "lock" and app == "mts" and not roles & {"finance_officer", "gm"}:
            return False
        if action in {"propose", "notify", "cancel"} and app == "inspections" and not roles & {"coordinator", "tech_manager", "gm"}:
            return False
        if action == "review" and app == "inspections" and not roles & {"coordinator", "quality_manager", "tech_manager", "gm"}:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if is_global_admin(request.user):
            return True
        model = obj.__class__
        return scoped_queryset(request.user, model.objects.filter(pk=obj.pk)).exists()


class ScopedAccessMixin:
    def get_queryset(self):
        base = super().get_queryset()
        return scoped_queryset(self.request.user, base)

    def _validate_related_scope(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        from django.db import models
        if is_global_admin(self.request.user):
            return
        for field, value in serializer.validated_data.items():
            if isinstance(value, models.Model):
                if not scoped_queryset(self.request.user, value.__class__.objects.filter(pk=value.pk)).exists():
                    raise PermissionDenied(f"You cannot link this record through field '{field}'.")
                continue
            if hasattr(serializer, "related_scope_fields") and field in serializer.related_scope_fields:
                foreign_key_lookup = {f"{field}_id": value}
                related_qs = value.__class__.objects.filter(**foreign_key_lookup)
                if not scoped_queryset(self.request.user, related_qs).exists():
                    raise PermissionDenied(f"You cannot link this record through field '{field}'.")


def filter_related_queryset(user, queryset):
    return scoped_queryset(user, queryset)
