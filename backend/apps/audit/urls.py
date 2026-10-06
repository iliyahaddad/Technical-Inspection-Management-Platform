from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditEventViewSet

router = DefaultRouter()
router.register(r'', AuditEventViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
]
