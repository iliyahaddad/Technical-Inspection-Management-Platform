from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.inspections.models import (
    InspectionRequest,
    RequestItem,
    InspectionNotification,
    ITP,
    ITPActivity,
    InspectorProfile,
    Certificate,
    Availability,
    Assignment,
    InspectionVisit,
)
from apps.accounts.serializers import UserSerializer

User = get_user_model()

class RequestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestItem
        fields = ['id', 'request', 'item_number', 'equipment_tag', 'description', 'material_type', 'specification', 'drawing_reference', 'quantity', 'unit', 'previously_inspected_qty', 'requested_qty', 'remarks']
        read_only_fields = ['id', 'request']

class InspectionRequestSerializer(serializers.ModelSerializer):
    items = RequestItemSerializer(many=True)

    class Meta:
        model = InspectionRequest
        fields = ['id', 'request_number', 'revision', 'project', 'submitted_by', 'contract', 'purchase_order', 'vendor', 'location', 'requested_inspection_date', 'discipline', 'inspection_type', 'inspection_level', 'priority', 'special_instructions', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at', 'review_comments', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'request_number', 'revision', 'submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at', 'review_comments', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs.get('status') == 'submitted' and not attrs.get('items'):
            raise serializers.ValidationError({'items': 'At least one inspection item is required.'})
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = InspectionRequest.objects.create(**validated_data)
        for item_data in items_data:
            RequestItem.objects.create(request=request, **item_data)
        return request

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                RequestItem.objects.create(request=instance, **item_data)
        return instance

class ITPActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ITPActivity
        fields = ['id', 'itp', 'activity_number', 'description', 'intervention_type', 'relevant_drawing', 'applicable_standard', 'acceptance_criteria', 'is_mandatory']
        read_only_fields = ['id', 'itp']

class ITPSerializer(serializers.ModelSerializer):
    activities = ITPActivitySerializer(many=True)

    class Meta:
        model = ITP
        fields = ['id', 'itp_number', 'title', 'revision', 'project', 'applicable_standard', 'activities', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        activities_data = validated_data.pop('activities', [])
        itp = ITP.objects.create(**validated_data)
        for activity_data in activities_data:
            ITPActivity.objects.create(itp=itp, **activity_data)
        return itp

class InspectionNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionNotification
        fields = ['id', 'notification_number', 'revision', 'inspection_request', 'project', 'vendor', 'location', 'inspection_date', 'inspection_type', 'itp', 'notice_period_days', 'status', 'issued_by', 'acknowledged_by', 'acknowledged_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'notification_number', 'revision', 'status', 'issued_by', 'acknowledged_by', 'acknowledged_at', 'created_at', 'updated_at']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'inspector', 'name', 'issuing_body', 'issue_date', 'expiry_date', 'certificate_number', 'file', 'has_file', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'file': {'write_only': True, 'required': False}}

    has_file = serializers.SerializerMethodField()

    def get_has_file(self, obj):
        return bool(obj.file)

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'inspector', 'date', 'is_available', 'note', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class InspectorProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True, read_only=True)
    availabilities = AvailabilitySerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = InspectorProfile
        fields = ['id', 'user', 'user_id', 'employee_number', 'employment_type', 'disciplines', 'specializations', 'years_of_experience', 'geographic_location', 'coverage_areas', 'travel_preferences', 'conflict_of_interest_declared', 'performance_score', 'is_active', 'certificates', 'availabilities', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        validated_data['user'] = user
        return InspectorProfile.objects.create(**validated_data)

class AssignmentSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source='inspector.user.get_full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'notification', 'inspector', 'inspector_name', 'proposed_by', 'approved_by', 'status', 'proposed_at', 'approved_at', 'notified_at', 'responded_at', 'completed_at', 'cancellation_reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'proposed_by', 'approved_by', 'status', 'proposed_at', 'approved_at', 'notified_at', 'responded_at', 'completed_at', 'created_at', 'updated_at']

class InspectionVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionVisit
        fields = ['id', 'assignment', 'visit_number', 'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end', 'location', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'visit_number', 'created_at', 'updated_at']
