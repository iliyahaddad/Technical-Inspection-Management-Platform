from config.access_control import ScopedAccessMixin, RoleAndScopePermission
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.clients.models import Client
from apps.clients.serializers import ClientSerializer

class ClientViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [RoleAndScopePermission]
