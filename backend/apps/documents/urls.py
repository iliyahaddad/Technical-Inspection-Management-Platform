from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.documents.views import DocumentViewSet, InspectionReportPdfView, FinancialStatementPdfView

router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/<int:report_id>/pdf/', InspectionReportPdfView.as_view(), name='report-pdf'),
    path('statements/<int:statement_id>/pdf/', FinancialStatementPdfView.as_view(), name='statement-pdf'),
]
