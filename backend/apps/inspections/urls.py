from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.inspections.views import (
    InspectionRequestViewSet,
    InspectionNotificationViewSet,
    ITPViewSet,
    ITPActivityViewSet,
    InspectorProfileViewSet,
    CertificateViewSet,
    AvailabilityViewSet,
    AssignmentViewSet,
    InspectionVisitViewSet,
)

router = DefaultRouter()
router.register(r'requests', InspectionRequestViewSet, basename='inspectionrequest')
router.register(r'notifications', InspectionNotificationViewSet, basename='inspectionnotification')
router.register(r'itps', ITPViewSet, basename='itp')
router.register(r'itp-activities', ITPActivityViewSet, basename='itpactivity')
router.register(r'inspectors', InspectorProfileViewSet, basename='inspectorprofile')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'availabilities', AvailabilityViewSet, basename='availability')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'visits', InspectionVisitViewSet, basename='inspectionvisit')

urlpatterns = [
    path('', include(router.urls)),
]
