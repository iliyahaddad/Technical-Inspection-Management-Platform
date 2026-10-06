# Database Entity Relationship Diagram

## Core Entities

```mermaid
erDiagram
    CompanySettings ||--|| User : "has_admin"
    User ||--o{ Role : "assigned"
    User ||--o{ ClientUser : "belongs_to"
    Client ||--o{ ClientUser : "has"
    Client ||--o{ Project : "owns"
    Project ||--o{ Contract : "has"
    Contract ||--o{ ContractRevision : "revised_as"
    Project ||--o{ PurchaseOrder : "has"
    Vendor ||--o{ PurchaseOrder : "fulfills"
    Vendor ||--o{ Location : "operates_at"
    Project ||--o{ InspectionRequest : "contains"
    ClientUser ||--o{ InspectionRequest : "submits"
    InspectionRequest ||--o{ RequestItem : "contains"
    InspectionRequest ||--o{ InspectionNotification : "generates"
    InspectionNotification ||--o{ ITP : "references"
    ITP ||--o{ ITPActivity : "contains"
    InspectorProfile ||--|| User : "linked_to"
    InspectorProfile ||--o{ Qualification : "holds"
    InspectorProfile ||--o{ Certificate : "certified_by"
    InspectorProfile ||--o{ Availability : "has"
    InspectorProfile ||--o{ Assignment : "assigned_to"
    Assignment ||--|| InspectionNotification : "for"
    Assignment ||--|| InspectorProfile : "assigns"
    Assignment ||--o{ InspectionVisit : "results_in"
    InspectionVisit ||--o{ InspectionTemplate : "uses"
    InspectionTemplate ||--o{ TemplateVersion : "versioned_as"
    InspectionVisit ||--o{ InspectionReport : "produces"
    InspectionReport ||--o{ ReportRevision : "revised_as"
    ReportRevision ||--o{ ChecklistAnswer : "contains"
    ReportRevision ||--o{ Measurement : "contains"
    ReportRevision ||--o{ Attachment : "has"
    ReportRevision ||--o{ SignatureRecord : "signed_by"
    InspectionVisit ||--o{ NCR : "may_generate"
    NCR ||--o{ CorrectiveAction : "requires"
    InspectorProfile ||--o{ Timesheet : "submits"
    Timesheet ||--o{ TimesheetEntry : "contains"
    TimesheetEntry ||--o{ InspectionVisit : "for"
    InspectorProfile ||--o{ Expense : "claims"
    Contract ||--o{ RateCard : "priced_by"
    RateCard ||--o{ RateRevision : "revised_as"
    CurrencyRate ||--o{ RateRevision : "applied_in"
    Project ||--o{ FinancialStatement : "reported_in"
    FinancialStatement ||--o{ StatementLine : "contains"
    StatementLine ||--o{ TimesheetEntry : "references"
    StatementLine ||--o{ Expense : "references"
    StatementLine ||--o{ Assignment : "references"
    InvoiceReference ||--o{ StatementLine : "covers"
    PaymentRecord ||--o{ FinancialStatement : "applied_to"
    User ||--o{ SignatureRecord : "signs"
    SignatureRecord ||--|| ReportRevision : "on"
    User ||--o{ ApprovalRecord : "performs"
    ApprovalRecord ||--|| InspectionRequest : "for"
    ApprovalRecord ||--|| InspectionReport : "for"
    ApprovalRecord ||--|| Timesheet : "for"
    Notification ||--o{ User : "sent_to"
    Notification ||--|| Assignment : "regarding"
    AuditEvent ||--o{ User : "performed_by"
    DocumentSequence ||--o{ User : "managed_by"
```

## Entity Summary

| Entity | Purpose |
|--------|---------|
| CompanySettings | Singleton configuration for the operating company |
| User | Authentication and identity for all platform users |
| Role | Configurable permission sets |
| Client | External client organizations |
| ClientUser | Client-side users mapped to clients |
| Project | Client-owned projects with unique codes |
| Contract | Legal and financial agreement with versioning |
| PurchaseOrder | Client or company purchase orders |
| Vendor | External vendors and manufacturers |
| Location | Inspection sites and factories |
| InspectionRequest | Client-submitted digital IRF |
| RequestItem | Line items within an inspection request |
| InspectionNotification | Generated notice for scheduling |
| ITP / ITPActivity | Inspection and Test Plan with intervention points |
| InspectorProfile | Extended profile for inspectors |
| Qualification / Certificate | Inspector competencies and expiry |
| Availability | Inspector calendar and scheduling |
| Assignment | Inspector-to-notification binding |
| InspectionVisit | Physical or remote inspection event |
| InspectionTemplate / TemplateVersion | Configurable dynamic form templates |
| InspectionReport / ReportRevision | Issued inspection reports with revision control |
| ChecklistAnswer / Measurement | Form response data |
| Attachment | Secure document and photo storage |
| Instrument | Calibrated equipment registry |
| NCR / CorrectiveAction | Nonconformity and remediation tracking |
| Timesheet / TimesheetEntry | Inspector time recording |
| Expense | Inspector and project expenses |
| RateCard / RateRevision | Versioned pricing rules |
| CurrencyRate | Exchange rate history |
| FinancialStatement / StatementLine | MTS financial output |
| InvoiceReference / PaymentRecord | Revenue tracking |
| SignatureRecord | Tamper-evident signature bindings |
| ApprovalRecord | Workflow approval audit |
| Notification | Communication events |
| AuditEvent | Immutable operation log |
| DocumentSequence | Controlled numbering |
