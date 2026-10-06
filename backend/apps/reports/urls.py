from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reports.views import (
    InspectionReportViewSet,
    ReportRevisionViewSet,
    ChecklistAnswerViewSet,
    MeasurementViewSet,
    AttachmentViewSet,
    InstrumentViewSet,
    InspectionTemplateViewSet,
    TemplateVersionViewSet,
    NCRViewSet,
    CorrectiveActionViewSet,
    ReleaseNoteViewSet,
)

router = DefaultRouter()
router.register(r'reports', InspectionReportViewSet, basename='inspectionreport')
router.register(r'revisions', ReportRevisionViewSet, basename='reportrevision')
router.register(r'checklist-answers', ChecklistAnswerViewSet, basename='checklistanswer')
router.register(r'measurements', MeasurementViewSet, basename='measurement')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'instruments', InstrumentViewSet, basename='instrument')
router.register(r'templates', InspectionTemplateViewSet, basename='inspectiontemplate')
router.register(r'template-versions', TemplateVersionViewSet, basename='templateversion')
router.register(r'ncrs', NCRViewSet, basename='ncr')
router.register(r'corrective-actions', CorrectiveActionViewSet, basename='correctiveaction')
router.register(r'release-notes', ReleaseNoteViewSet, basename='releasenote')

urlpatterns = [
    path('', include(router.urls)),
]
