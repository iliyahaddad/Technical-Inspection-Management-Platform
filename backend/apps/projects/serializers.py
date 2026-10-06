from rest_framework import serializers
from apps.projects.models import Project, Contract, ContractRevision
from apps.clients.serializers import ClientSerializer

class ContractRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractRevision
        fields = ['id', 'contract', 'revision_number', 'change_description', 'effective_date', 'supporting_document', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']

class ContractSerializer(serializers.ModelSerializer):
    revisions = ContractRevisionSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = ['id', 'project', 'contract_number', 'title', 'description', 'contract_type', 'total_value', 'currency', 'start_date', 'end_date', 'status', 'version', 'revisions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.IntegerField(write_only=True)
    contracts = ContractSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'client', 'client_id', 'project_code', 'name', 'description', 'project_manager', 'status', 'start_date', 'end_date', 'contract_value', 'currency', 'contracts', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
