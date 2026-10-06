from rest_framework import serializers
from apps.mts.models import (
    Timesheet,
    TimesheetEntry,
    Expense,
    RateCard,
    RateRevision,
    CurrencyRate,
    FinancialStatement,
    StatementLine,
    InvoiceReference,
    PaymentRecord,
    SignatureRecord,
    ApprovalRecord,
    CostLedger,
)

class TimesheetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimesheetEntry
        fields = ['id', 'timesheet', 'work_date', 'start_time', 'end_time', 'break_duration', 'actual_hours', 'travel_hours', 'waiting_hours', 'overtime_hours', 'location', 'description', 'visit', 'created_at']
        read_only_fields = ['id', 'created_at']

class TimesheetSerializer(serializers.ModelSerializer):
    entries = TimesheetEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Timesheet
        fields = ['id', 'inspector', 'project', 'assignment', 'month', 'status', 'submitted_at', 'approved_by', 'approved_at', 'entries', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'submitted_at', 'approved_by', 'approved_at', 'created_at', 'updated_at']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'inspector', 'project', 'assignment', 'expense_date', 'category', 'amount', 'currency', 'description', 'receipt', 'has_receipt', 'status', 'submitted_at', 'approved_by', 'approved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'submitted_at', 'approved_by', 'approved_at', 'created_at', 'updated_at']
        extra_kwargs = {'receipt': {'write_only': True, 'required': False}}

    has_receipt = serializers.SerializerMethodField()

    def get_has_receipt(self, obj):
        return bool(obj.receipt)

    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

class RateRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateRevision
        fields = ['id', 'rate_card', 'revision_number', 'rate_type', 'unit', 'amount', 'currency', 'min_chargeable_unit', 'overtime_multiplier', 'travel_multiplier', 'effective_date', 'created_at']
        read_only_fields = ['id', 'rate_card', 'created_at']

class RateCardSerializer(serializers.ModelSerializer):
    revisions = RateRevisionSerializer(many=True)

    class Meta:
        model = RateCard
        fields = ['id', 'contract', 'name', 'billing_model', 'currency', 'region', 'effective_date', 'expiry_date', 'is_active', 'revisions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        revisions_data = validated_data.pop('revisions', [])
        rate_card = RateCard.objects.create(**validated_data)
        for revision_data in revisions_data:
            RateRevision.objects.create(rate_card=rate_card, **revision_data)
        return rate_card

class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = ['id', 'from_currency', 'to_currency', 'rate', 'effective_date', 'created_at']
        read_only_fields = ['id', 'created_at']

class StatementLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementLine
        fields = ['id', 'statement', 'line_type', 'reference_type', 'reference_id', 'description', 'quantity', 'unit_rate', 'amount', 'currency', 'created_at']
        read_only_fields = ['id', 'statement', 'created_at']

class FinancialStatementSerializer(serializers.ModelSerializer):
    lines = StatementLineSerializer(many=True, required=False)

    class Meta:
        model = FinancialStatement
        fields = ['id', 'project', 'statement_number', 'period_start', 'period_end', 'currency', 'total_billable', 'total_invoiced', 'current_amount', 'tax_amount', 'total_due', 'status', 'approved_by', 'approved_at', 'locked_at', 'lines', 'created_at', 'updated_at']
        read_only_fields = ['id', 'statement_number', 'approved_by', 'approved_at', 'locked_at', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        from apps.projects.models import Contract
        from apps.mts.services import BillingEngine
        lines_data = validated_data.pop('lines', [])
        statement = FinancialStatement.objects.create(**validated_data)
        BillingEngine.check_double_billing(
            project_id=statement.project_id,
            source_type='statement',
            source_id=str(statement.id),
            period_start=statement.period_start,
            period_end=statement.period_end,
            exclude_source_id=str(statement.id),
        )
        try:
            contract = Contract.objects.filter(project=statement.project).order_by('-version').first()
            if contract:
                BillingEngine.check_allocation_ratio(contract, [type('Line', (), {'line_type': l.get('line_type', ''), 'amount': l.get('amount', 0)}) for l in lines_data])
        except Exception:
            pass
        for line_data in lines_data:
            StatementLine.objects.create(statement=statement, **line_data)
        return statement

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                StatementLine.objects.create(statement=instance, **line_data)
        return instance

class InvoiceReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceReference
        fields = ['id', 'statement', 'invoice_number', 'invoice_date', 'amount', 'currency', 'created_at']
        read_only_fields = ['id', 'created_at']

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = ['id', 'statement', 'payment_date', 'amount', 'currency', 'reference', 'created_at']
        read_only_fields = ['id', 'created_at']

class SignatureRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatureRecord
        fields = ['id', 'user', 'document_type', 'document_id', 'revision', 'image', 'content_hash', 'ip_address', 'user_agent', 'signed_at']
        read_only_fields = ['id', 'signed_at']

class ApprovalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRecord
        fields = ['id', 'user', 'object_type', 'object_id', 'action', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at']

class CostLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostLedger
        fields = ['id', 'project', 'source_type', 'source_id', 'amount', 'currency', 'cost_date', 'created_at']
        read_only_fields = ['id', 'created_at']
