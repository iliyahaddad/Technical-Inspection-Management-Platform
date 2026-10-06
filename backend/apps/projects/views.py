from config.access_control import ScopedAccessMixin, RoleAndScopePermission
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.projects.models import Project, Contract
from apps.projects.serializers import ProjectSerializer, ContractSerializer

class ProjectViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [RoleAndScopePermission]

class ContractViewSet(ScopedAccessMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [RoleAndScopePermission]
