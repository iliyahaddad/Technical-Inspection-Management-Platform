from django.db import models

class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Assignment(models.Model):
    pass

class ITP(models.Model):
    pass

class ITPActivity(models.Model):
    pass

class InspectorProfile(models.Model):
    pass

class Certificate(models.Model):
    pass

class Availability(models.Model):
    pass

class InspectionVisit(models.Model):
    pass

class InspectionTemplate(models.Model):
    pass

class TemplateVersion(models.Model):
    pass

class InspectionReport(models.Model):
    pass

class ReportRevision(models.Model):
    pass

class ChecklistAnswer(models.Model):
    pass

class Measurement(models.Model):
    pass

class Attachment(models.Model):
    pass

class Instrument(models.Model):
    pass

class NCR(models.Model):
    pass

class CorrectiveAction(models.Model):
    pass

class ReleaseNote(models.Model):
    pass

class Timesheet(models.Model):
    pass

class TimesheetEntry(models.Model):
    pass

class Expense(models.Model):
    pass

class RateCard(models.Model):
    pass

class RateRevision(models.Model):
    pass

class CurrencyRate(models.Model):
    pass

class FinancialStatement(models.Model):
    pass

class StatementLine(models.Model):
    pass

class InvoiceReference(models.Model):
    pass

class PaymentRecord(models.Model):
    pass

class SignatureRecord(models.Model):
    pass

class ApprovalRecord(models.Model):
    pass

class AuditEvent(models.Model):
    pass

class DocumentSequence(models.Model):
    pass
