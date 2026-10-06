from rest_framework import serializers
from apps.reports.models import (
    InspectionReport,
    ReportRevision,
    ChecklistAnswer,
    Measurement,
    Attachment,
    Instrument,
    InspectionTemplate,
    TemplateVersion,
    NCR,
    CorrectiveAction,
    ReleaseNote,
)
from apps.accounts.serializers import UserSerializer

class ReportRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRevision
        fields = ['id', 'report', 'revision_number', 'content', 'content_hash', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'content_hash', 'created_at']

class InspectionReportSerializer(serializers.ModelSerializer):
    revisions = ReportRevisionSerializer(many=True, read_only=True)

    class Meta:
        model = InspectionReport
        fields = ['id', 'report_number', 'revision', 'inspection_visit', 'template_version', 'submitted_by', 'status', 'scope', 'inspected_qty', 'accepted_qty', 'rejected_qty', 'remaining_qty', 'instruments_used', 'narrative', 'deviations', 'recommendations', 'submitted_at', 'reviewed_by', 'reviewed_at', 'review_comments', 'issued_at', 'issued_by', 'content_hash', 'revisions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'report_number', 'revision', 'submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at', 'review_comments', 'issued_by', 'issued_at', 'status', 'content_hash', 'created_at', 'updated_at']

class ChecklistAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistAnswer
        fields = ['id', 'report_revision', 'activity_id', 'answer', 'remarks', 'created_at']
        read_only_fields = ['id', 'created_at']

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['id', 'report_revision', 'parameter', 'value', 'unit', 'tolerance', 'result', 'created_at']
        read_only_fields = ['id', 'created_at']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'report_revision', 'file', 'filename', 'file_size', 'content_type', 'description', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'filename', 'file_size', 'content_type', 'uploaded_by', 'uploaded_at']
        extra_kwargs = {'file': {'write_only': True}}

class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['id', 'name', 'serial_number', 'calibration_date', 'expiry_date', 'certificate_number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class InspectionTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionTemplate
        fields = ['id', 'name', 'discipline', 'version', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TemplateVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateVersion
        fields = ['id', 'template', 'version_number', 'schema', 'created_at']
        read_only_fields = ['id', 'created_at']

class NCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = NCR
        fields = ['id', 'ncr_number', 'inspection_visit', 'report_revision', 'itp_activity', 'description', 'requirement_reference', 'evidence', 'severity', 'responsible_party', 'proposed_corrective_action', 'root_cause', 'target_completion_date', 'status', 'closed_at', 'closed_by', 'closure_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'ncr_number', 'status', 'closed_at', 'closed_by', 'closure_notes', 'created_at', 'updated_at']

class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = ['id', 'ncr', 'description', 'assigned_to', 'due_date', 'completed_at', 'evidence', 'created_at', 'updated_at']
        read_only_fields = ['id', 'completed_at', 'created_at', 'updated_at']

class ReleaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseNote
        fields = ['id', 'release_number', 'inspection_visit', 'released_by', 'notes', 'is_final', 'released_at']
        read_only_fields = ['id', 'release_number', 'released_at']
