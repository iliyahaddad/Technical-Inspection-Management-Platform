from config.access_control import ScopedAccessMixin, RoleAndScopePermission
from config.workflow import LockedStatusMixin, TransitionMixin
from apps.documents.responses import protected_file_response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from apps.inspections.models import (
    InspectionRequest,
    InspectionNotification,
    ITP,
    ITPActivity,
    InspectorProfile,
    Certificate,
    Availability,
    Assignment,
    InspectionVisit,
)
from apps.inspections.serializers import (
    InspectionRequestSerializer,
    InspectionNotificationSerializer,
    ITPSerializer,
    ITPActivitySerializer,
    InspectorProfileSerializer,
    CertificateSerializer,
    AvailabilitySerializer,
    AssignmentSerializer,
    InspectionVisitSerializer,
)

class InspectionRequestViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'submitted', 'under_review', 'accepted', 'rejected', 'ready_for_scheduling'})
    queryset = InspectionRequest.objects.all()
    serializer_class = InspectionRequestSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        self._validate_related_scope(serializer)
        serializer.save(submitted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.status not in ('draft', 'clarification_required'):
            return Response({'detail': 'Only draft requests (or requests returned for clarification) can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'submitted'
        instance.submitted_at = timezone.now()
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    REVIEW_DECISIONS = {
        'accept': 'accepted', 'accepted': 'accepted',
        'reject': 'rejected', 'rejected': 'rejected',
        'clarification': 'clarification_required', 'clarification_required': 'clarification_required',
    }

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        instance = self.get_object()
        # Frontend and API clients may send either the verb or the resulting status.
        decision = request.data.get('decision') or request.data.get('action')
        new_status = self.REVIEW_DECISIONS.get(decision)
        if new_status is None:
            return Response({'detail': 'Invalid decision.'}, status=status.HTTP_400_BAD_REQUEST)
        if instance.status not in ('submitted', 'under_review'):
            return Response({'detail': 'Only submitted requests can be reviewed.'}, status=status.HTTP_400_BAD_REQUEST)
        comments = request.data.get('comments', '')
        if new_status in ('rejected', 'clarification_required') and not str(comments).strip():
            return Response({'comments': 'A comment is required when rejecting or asking for clarification.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = new_status
        instance.reviewed_by = request.user
        instance.reviewed_at = timezone.now()
        instance.review_comments = comments
        instance.save()
        return Response(self.get_serializer(instance).data)

class InspectionNotificationViewSet(TransitionMixin, LockedStatusMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    locked_statuses = frozenset({'issued', 'acknowledged', 'cancelled'})
    queryset = InspectionNotification.objects.all()
    serializer_class = InspectionNotificationSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        self._validate_related_scope(serializer)
        serializer.save(issued_by=self.request.user)

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'draft':
            return Response({'detail': 'Only draft notifications can be issued.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'issued'
        instance.issued_by = request.user
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'issued':
            return Response({'detail': 'Only issued notifications can be acknowledged.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'acknowledged'
        instance.acknowledged_by = request.user
        instance.acknowledged_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

class ITPViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = ITP.objects.all()
    serializer_class = ITPSerializer
    permission_classes = [RoleAndScopePermission]

class ITPActivityViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = ITPActivity.objects.all()
    serializer_class = ITPActivitySerializer
    permission_classes = [RoleAndScopePermission]

class InspectorProfileViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = InspectorProfile.objects.all()
    serializer_class = InspectorProfileSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=False, methods=['get'])
    def search(self, request):
        discipline = request.query_params.get('discipline')
        location = request.query_params.get('location')
        queryset = self.get_queryset().filter(is_active=True)
        if discipline:
            queryset = queryset.filter(disciplines__contains=[discipline])
        if location:
            queryset = queryset.filter(geographic_location__icontains=location)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CertificateViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        return protected_file_response(self.get_object().file)

class AvailabilityViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [RoleAndScopePermission]

class AssignmentViewSet(TransitionMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [RoleAndScopePermission]

    def perform_create(self, serializer):
        self._validate_related_scope(serializer)
        serializer.save(proposed_by=self.request.user)

    @action(detail=True, methods=['post'])
    def propose(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'proposed':
            return Response({'detail': 'Assignment is not in proposed state.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'approved'
        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'approved':
            return Response({'detail': 'Assignment must be approved before notification.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'notified'
        instance.notified_at = timezone.now()
        instance.save()
        from apps.notifications.tasks import notify_assignment
        notify_assignment(instance)
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'notified':
            return Response({'detail': 'Assignment must be notified before acceptance.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'accepted'
        instance.responded_at = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'notified':
            return Response({'detail': 'Assignment must be notified before decline.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'declined'
        instance.responded_at = timezone.now()
        instance.cancellation_reason = request.data.get('reason', '')
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        instance = self.get_object()
        if instance.status in ['completed', 'cancelled']:
            return Response({'detail': 'Cannot cancel a completed or already cancelled assignment.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'cancelled'
        instance.cancellation_reason = request.data.get('reason', '')
        instance.save()
        return Response(self.get_serializer(instance).data)

class InspectionVisitViewSet(TransitionMixin, ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = InspectionVisit.objects.all()
    serializer_class = InspectionVisitSerializer
    permission_classes = [RoleAndScopePermission]

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'scheduled':
            return Response({'detail': 'Only scheduled visits can be started.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'in_progress'
        instance.actual_start = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        instance = self.get_object()
        if instance.status != 'in_progress':
            return Response({'detail': 'Only in-progress visits can be completed.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'completed'
        instance.actual_end = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)
