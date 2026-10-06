# ISO/IEC 17020 Compliance Documentation

## Scope

This document describes how the Technical Inspection Management Platform supports the operational requirements of ISO/IEC 17020 (Conformity assessment — Requirements for the operation of various types of bodies performing inspection).

## Important Disclaimer

Software functionality alone does not establish certification or accreditation. The system supports compliance by providing the necessary tools, traceability, and controls. The organization must still implement its own quality management system, employ qualified personnel, and undergo external assessment by a competent accreditation body.

## Key ISO/IEC 17020 Requirements and System Support

### 1. Impartiality (Clause 4)

| Requirement | System Support |
|-------------|----------------|
| Inspection bodies shall be impartial | Role-based access control restricts data access by role and client ownership |
| No conflicts of interest | Inspector profiles include conflict-of-interest declarations |
| No inspector approves their own report | Report approval workflow requires independent reviewer |

### 2. Competence (Clause 5)

| Requirement | System Support |
|-------------|----------------|
| Personnel with appropriate qualifications | InspectorProfile model tracks qualifications, certificates, disciplines |
| Certificate validity monitoring | Certificate model includes expiry_date field |
| Training and experience records | Years of experience, specializations fields |
| Performance evaluation | Performance score field on InspectorProfile |

### 3. Inspection Process (Clause 6)

| Requirement | System Support |
|-------------|----------------|
| Defined inspection procedures | ITP and ITPActivity models define inspection activities |
| Inspection plans | InspectionRequest and InspectionNotification models |
| Equipment and instrument control | Instrument model with calibration tracking |
| Inspection records | InspectionReport with revision history |
| Nonconformity handling | NCR and CorrectiveAction models |

### 4. Documents and Records (Clause 7)

| Requirement | System Support |
|-------------|----------------|
| Document control | Document model with versioning and approval status |
| Record retention | AuditEvent model provides complete audit trail |
| Report revision control | ReportRevision model preserves all versions |
| Immutability after issuance | Report status workflow prevents modification after issuance |

### 5. Inspection Items and Methods (Clause 8)

| Requirement | System Support |
|-------------|----------------|
| Defined inspection methods | InspectionTemplate with versioned dynamic forms |
| Acceptance criteria | ChecklistAnswer with pass/fail criteria |
| Measurement records | Measurement model linked to report revisions |
| Deviation handling | NCR references in reports |

### 6. Equipment (Clause 9)

| Requirement | System Support |
|-------------|----------------|
| Suitable equipment | Instrument model with calibration status |
| Calibration records | Certificate model linked to inspectors |
| Maintenance tracking | Instrument calibration_date and expiry_date |

### 7. External Providers and Temporary Personnel (Clause 10)

| Requirement | System Support |
|-------------|----------------|
| Qualification verification | InspectorProfile with employment_type and qualifications |
| Subcontractor management | Vendor model for subcontractors |

### 8. Handling of Inspection Items (Clause 11)

| Requirement | System Support |
|-------------|----------------|
| Protection of items | Assignment and Visit tracking |
| Condition reporting | InspectionReport with narrative and deviations |

### 9. Inspection Data and Reporting (Clause 12)

| Requirement | System Support |
|-------------|----------------|
| Accurate data recording | Structured models with validation |
| Report generation | Branded PDF reports with Persian/English support |
| Traceability | AuditEvent for all operations |

## Audit Trail

The system maintains a complete audit trail via the AuditEvent model:

- Every create, update, and delete operation is logged
- User identity, timestamp, IP address, and user agent are recorded
- Changes are stored as JSON diffs
- Audit events cannot be modified or deleted

## Data Integrity

- Database constraints enforce referential integrity
- Transaction boundaries protect critical operations (document numbering, approvals, financial posting)
- Report content hash ensures document integrity
- Signature records bind to exact document revision and content hash

## Limitations

- The system does not replace the need for a quality management system
- Software cannot verify the competence of personnel
- Electronic signatures are not legally qualified digital signatures
- The system does not perform physical inspections
- ISO 17020 compliance requires organizational processes beyond software

## Recommended Actions

1. Implement a quality manual describing inspection procedures
2. Train all users on ISO 17020 requirements
3. Establish internal audit procedures
4. Maintain equipment calibration schedules
5. Review and approve all financial formulas by authorized users
6. Conduct periodic competency assessments for inspectors
7. Implement document retention policies per regulatory requirements
