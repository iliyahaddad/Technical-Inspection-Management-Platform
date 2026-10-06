from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.clients.views import ClientViewSet

router = DefaultRouter()
router.register(r'', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
