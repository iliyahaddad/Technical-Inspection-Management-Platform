from django.db import transaction
from django.core.exceptions import ValidationError
from apps.mts.models import FinancialStatement, StatementLine, CostLedger

class BillingEngine:
    @staticmethod
    def check_double_billing(project_id, source_type, source_id, period_start, period_end, exclude_source_id=None):
        existing = FinancialStatement.objects.filter(
            project_id=project_id,
            status__in=['draft', 'approved', 'sent'],
            period_start__lte=period_end,
            period_end__gte=period_start,
        )
        if exclude_source_id:
            existing = existing.exclude(id=exclude_source_id)
        if existing.exists():
            raise ValidationError('A financial statement already exists for this project in the specified period.')

    @staticmethod
    def check_allocation_ratio(contract, lines):
        if contract.contract_type != 'mixed':
            return
        total = sum(float(line.amount) for line in lines)
        person_day_total = sum(float(line.amount) for line in lines if line.line_type == 'person_day')
        fixed_visit_total = sum(float(line.amount) for line in lines if line.line_type == 'fixed_visit')
        if total > 0:
            person_day_ratio = person_day_total / total
            fixed_visit_ratio = fixed_visit_total / total
            if person_day_ratio > 0.8 or fixed_visit_ratio > 0.8:
                raise ValidationError('Mixed contract allocation ratio exceeds allowed limits.')

    @staticmethod
    def generate_statement(project_id, period_start, period_end, currency='IRR'):
        with transaction.atomic():
            statement = FinancialStatement.objects.create(
                project_id=project_id,
                period_start=period_start,
                period_end=period_end,
                currency=currency,
                total_billable=0,
                total_invoiced=0,
                current_amount=0,
                total_due=0,
            )
            return statement

    @staticmethod
    def add_cost_to_ledger(timesheet_or_expense):
        CostLedger.objects.create(
            project=timesheet_or_expense.project,
            source_type='timesheet' if hasattr(timesheet_or_expense, 'entries') else 'expense',
            source_id=str(timesheet_or_expense.id),
            amount=timesheet_or_expense.amount if hasattr(timesheet_or_expense, 'amount') else sum(e.actual_hours for e in timesheet_or_expense.entries.all()),
            currency=timesheet_or_expense.currency,
            cost_date=timesheet_or_expense.expense_date if hasattr(timesheet_or_expense, 'expense_date') else timesheet_or_expense.month,
        )
