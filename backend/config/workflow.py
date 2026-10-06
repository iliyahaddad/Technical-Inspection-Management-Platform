"""Shared workflow guards for state-machine style viewsets.

* ``LockedStatusMixin``  - records past a given status are immutable through the generic
  update/delete endpoints (ISO 17020 style record control); only explicit workflow actions
  may change them.
* ``ChildLockMixin``     - child rows (timesheet entries, statement lines, ...) inherit the
  lock of their parent.
* ``TransitionMixin``    - workflow actions run on a row-locked fresh copy of the object, so two
  concurrent approvals cannot both succeed.
* ``forbid_self_review`` - separation of duties: the person who produced a record must not
  approve it.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This record is locked and can no longer be modified."
    default_code = "record_locked"


def bad_transition(message):
    return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)


def forbid_self_review(request, owner_user_id, what="record"):
    """Raise PermissionDenied if the acting user is the author/owner of the record."""
    if owner_user_id is not None and owner_user_id == request.user.pk:
        raise PermissionDenied(f"Separation of duties: you cannot approve or review your own {what}.")


class LockedStatusMixin:
    locked_statuses = frozenset()
    status_field = "status"

    def _assert_unlocked(self, instance):
        if getattr(instance, self.status_field, None) in self.locked_statuses:
            raise Conflict()

    def perform_update(self, serializer):
        self._assert_unlocked(serializer.instance)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._assert_unlocked(instance)
        super().perform_destroy(instance)


class ChildLockMixin:
    """Lock child rows while their parent is in a locked status. ``parent_field`` is the FK name."""
    parent_field = None
    parent_locked_statuses = frozenset()

    def _assert_parent_unlocked(self, parent):
        if parent is not None and getattr(parent, "status", None) in self.parent_locked_statuses:
            raise Conflict("The parent record is locked; its items can no longer be modified.")

    def perform_create(self, serializer):
        self._assert_parent_unlocked(serializer.validated_data.get(self.parent_field))
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self._assert_parent_unlocked(getattr(serializer.instance, self.parent_field))
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._assert_parent_unlocked(getattr(instance, self.parent_field))
        super().perform_destroy(instance)


class TransitionMixin:
    """For detail POST actions return a ``SELECT ... FOR UPDATE`` copy of the object.

    Authorisation and tenant scoping are still enforced by ``super().get_object()``; the
    re-fetch is by primary key on the plain manager because the scoped queryset uses DISTINCT,
    which PostgreSQL does not allow together with FOR UPDATE.
    """

    def get_object(self):
        obj = super().get_object()
        if self.request.method == "POST" and getattr(self, "action", None) not in (None, "create"):
            with transaction.atomic():
                obj = type(obj)._default_manager.select_for_update().get(pk=obj.pk)
        return obj
