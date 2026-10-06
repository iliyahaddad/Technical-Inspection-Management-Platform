# Data Dictionary

## Table: CompanySettings
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| name | varchar(255) | NO | Company legal name |
| trade_name | varchar(255) | YES | Operating trade name |
| logo | varchar(1024) | YES | Logo file path or URL |
| address | text | YES | Registered address |
| default_timezone | varchar(64) | NO | Default business timezone (e.g., Asia/Tehran) |
| default_currency | char(3) | NO | Default currency code (e.g., IRR) |
| fiscal_year_start | date | NO | Fiscal year start date |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: User
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| email | varchar(255) | NO | Unique login email |
| phone | varchar(32) | YES | Contact phone |
| first_name | varchar(128) | NO | Given name |
| last_name | varchar(128) | NO | Family name |
| preferred_language | char(2) | NO | 'fa' or 'en' |
| date_format | varchar(32) | NO | 'jalali' or 'gregorian' |
| is_active | boolean | NO | Soft delete / disable flag |
| is_staff | boolean | NO | Django admin access |
| is_superuser | boolean | NO | Full system access |
| last_login | datetime | YES | Last authentication timestamp |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: Role
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| name | varchar(128) | NO | Unique role name (e.g., 'inspection_coordinator') |
| display_name_fa | varchar(128) | NO | Persian display name |
| display_name_en | varchar(128) | NO | English display name |
| description | text | YES | Role purpose and scope |
| is_system | boolean | NO | Protected system role |

## Table: Client
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| name | varchar(255) | NO | Legal company name |
| trade_name | varchar(255) | YES | Operating name |
| registration_number | varchar(64) | YES | Business registration |
| tax_number | varchar(64) | YES | Tax identifier |
| address | text | YES | Registered address |
| billing_address | text | YES | Invoice address |
| contact_email | varchar(255) | YES | Primary contact email |
| contact_phone | varchar(32) | YES | Primary contact phone |
| is_active | boolean | NO | Active client flag |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: ClientUser
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| user_id | bigint | NO | FK -> User |
| client_id | bigint | NO | FK -> Client |
| role | varchar(64) | NO | 'admin', 'requester', 'approver' |
| is_primary | boolean | NO | Primary contact for client |
| created_at | datetime | NO | UTC timestamp |

## Table: Project
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| client_id | bigint | NO | FK -> Client |
| project_code | varchar(64) | NO | Unique project identifier |
| name | varchar(255) | NO | Project name |
| description | text | YES | Scope and objectives |
| project_manager_id | bigint | YES | FK -> User |
| status | varchar(32) | NO | 'draft', 'active', 'on_hold', 'completed', 'closed' |
| start_date | date | YES | Planned start |
| end_date | date | YES | Planned completion |
| contract_value | numeric(18,2) | YES | Total contracted value |
| currency | char(3) | NO | Contract currency |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: Contract
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| project_id | bigint | NO | FK -> Project |
| contract_number | varchar(64) | NO | Unique contract reference |
| title | varchar(255) | NO | Contract title |
| description | text | YES | Scope and terms summary |
| contract_type | varchar(32) | NO | 'person_day', 'fixed_visit', 'milestone', 'mixed' |
| total_value | numeric(18,2) | NO | Agreed total value |
| currency | char(3) | NO | Contract currency |
| start_date | date | NO | Contract effective date |
| end_date | date | NO | Contract expiry |
| status | varchar(32) | NO | 'draft', 'active', 'expired', 'terminated' |
| version | integer | NO | Concurrency version |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: ContractRevision
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| contract_id | bigint | NO | FK -> Contract |
| revision_number | varchar(32) | NO | Revision reference |
| change_description | text | NO | What changed |
| effective_date | date | NO | When revision takes effect |
| supporting_document | varchar(1024) | YES | File path |
| created_by_id | bigint | NO | FK -> User |
| created_at | datetime | NO | UTC timestamp |

## Table: InspectionRequest
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| request_number | varchar(64) | NO | Controlled sequence |
| revision | integer | NO | Revision counter |
| project_id | bigint | NO | FK -> Project |
| submitted_by_id | bigint | NO | FK -> User (client user) |
| contract_id | bigint | YES | FK -> Contract |
| purchase_order_id | bigint | YES | FK -> PurchaseOrder |
| vendor_id | bigint | YES | FK -> Vendor |
| location_id | bigint | YES | FK -> Location |
| requested_inspection_date | datetime | YES | Client requested date/time |
| discipline | varchar(64) | NO | Mechanical, electrical, etc. |
| inspection_type | varchar(64) | NO | Pre-shipment, in-process, etc. |
| inspection_level | varchar(16) | YES | I, II, III |
| priority | varchar(16) | NO | 'low', 'normal', 'high', 'urgent' |
| special_instructions | text | YES | Client notes |
| status | varchar(32) | NO | 'draft', 'submitted', 'under_review', 'clarification_required', 'accepted', 'rejected', 'ready_for_scheduling' |
| submitted_at | datetime | YES | When submitted |
| reviewed_by_id | bigint | YES | FK -> User (coordinator) |
| reviewed_at | datetime | YES | Review timestamp |
| review_comments | text | YES | Coordinator feedback |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: RequestItem
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| request_id | bigint | NO | FK -> InspectionRequest |
| item_number | integer | NO | Line sequence |
| equipment_tag | varchar(128) | YES | Tag identifier |
| description | varchar(255) | NO | Item description |
| material_type | varchar(128) | YES | Material or equipment type |
| specification | varchar(255) | YES | Technical specification |
| drawing_reference | varchar(255) | YES | Drawing number and revision |
| quantity | numeric(12,3) | NO | Total quantity |
| unit | varchar(32) | NO | Unit of measurement |
| previously_inspected_qty | numeric(12,3) | NO | Already inspected |
| requested_qty | numeric(12,3) | NO | Requested for this inspection |
| remarks | text | YES | Item-specific notes |

## Table: InspectionNotification
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| notification_number | varchar(64) | NO | Controlled sequence |
| revision | integer | NO | Revision counter |
| inspection_request_id | bigint | NO | FK -> InspectionRequest |
| project_id | bigint | NO | FK -> Project |
| vendor_id | bigint | YES | FK -> Vendor |
| location_id | bigint | YES | FK -> Location |
| inspection_date | datetime | NO | Scheduled date/time |
| inspection_type | varchar(64) | NO | Inspection type |
| itp_id | bigint | YES | FK -> ITP |
| notice_period_days | integer | NO | Configurable advance notice |
| status | varchar(32) | NO | 'draft', 'issued', 'acknowledged', 'in_progress', 'completed', 'cancelled' |
| issued_by_id | bigint | NO | FK -> User |
| acknowledged_by_id | bigint | YES | FK -> User (vendor/client) |
| acknowledged_at | datetime | YES | Acknowledgment timestamp |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: ITPActivity
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| itp_id | bigint | NO | FK -> ITP |
| activity_number | varchar(32) | NO | ITP line reference |
| description | varchar(255) | NO | Activity description |
| intervention_type | varchar(8) | NO | 'H', 'W', 'SW', 'M', 'R' |
| relevant_drawing | varchar(255) | YES | Drawing reference |
| applicable_standard | varchar(255) | YES | Standard reference |
| acceptance_criteria | text | YES | Pass/fail criteria |
| is_mandatory | boolean | NO | Blocking hold point |

## Table: InspectorProfile
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| user_id | bigint | NO | FK -> User |
| employee_number | varchar(64) | YES | Company ID |
| employment_type | varchar(32) | NO | 'employee', 'contractor' |
| disciplines | jsonb | NO | Array of technical disciplines |
| specializations | jsonb | YES | Detailed specializations |
| years_of_experience | numeric(4,1) | YES | Years in field |
| geographic_location | varchar(128) | YES | Base city/country |
| coverage_areas | jsonb | YES | Permitted work regions |
| travel_preferences | jsonb | YES | Travel constraints or preferences |
| conflict_of_interest_declared | boolean | NO | COI on file |
| performance_score | numeric(5,2) | YES | Internal rating |
| is_active | boolean | NO | Available for assignment |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: Certificate
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| inspector_id | bigint | NO | FK -> InspectorProfile |
| name | varchar(255) | NO | Certificate title |
| issuing_body | varchar(255) | NO | Issuing authority |
| issue_date | date | NO | Date issued |
| expiry_date | date | YES | Expiry date (null = no expiry) |
| certificate_number | varchar(128) | YES | Reference number |
| file | varchar(1024) | YES | Scanned copy path |
| created_at | datetime | NO | UTC timestamp |

## Table: Assignment
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| notification_id | bigint | NO | FK -> InspectionNotification |
| inspector_id | bigint | NO | FK -> InspectorProfile |
| proposed_by_id | bigint | NO | FK -> User (coordinator) |
| approved_by_id | bigint | YES | FK -> User (if approval required) |
| status | varchar(32) | NO | 'proposed', 'approved', 'notified', 'accepted', 'declined', 'confirmed', 'completed', 'cancelled' |
| proposed_at | datetime | NO | Proposal timestamp |
| approved_at | datetime | YES | Approval timestamp |
| notified_at | datetime | YES | Inspector notification timestamp |
| responded_at | datetime | YES | Inspector response timestamp |
| completed_at | datetime | YES | Completion timestamp |
| cancellation_reason | text | YES | If cancelled |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: InspectionVisit
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| assignment_id | bigint | NO | FK -> Assignment |
| visit_number | varchar(64) | NO | Controlled sequence |
| scheduled_start | datetime | NO | Planned start |
| scheduled_end | datetime | NO | Planned end |
| actual_start | datetime | YES | Actual start |
| actual_end | datetime | YES | Actual end |
| location_id | bigint | YES | FK -> Location |
| status | varchar(32) | NO | 'scheduled', 'in_progress', 'completed', 'postponed', 'cancelled' |
| notes | text | YES | Visit-level notes |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: InspectionReport
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| report_number | varchar(64) | NO | Controlled sequence |
| revision | integer | NO | Revision counter |
| inspection_visit_id | bigint | NO | FK -> InspectionVisit |
| template_version_id | bigint | NO | FK -> TemplateVersion |
| submitted_by_id | bigint | NO | FK -> User (inspector) |
| status | varchar(32) | NO | 'draft', 'submitted', 'under_review', 'revision_required', 'approved', 'issued' |
| scope | text | YES | Inspection scope narrative |
| inspected_qty | numeric(12,3) | YES | Total inspected quantity |
| accepted_qty | numeric(12,3) | YES | Accepted quantity |
| rejected_qty | numeric(12,3) | YES | Rejected quantity |
| remaining_qty | numeric(12,3) | YES | Remaining to inspect |
| instruments_used | jsonb | YES | Instruments with calibration status |
| narrative | text | YES | Detailed findings |
| deviations | text | YES | Deviations and observations |
| recommendations | text | YES | Recommendations for follow-up |
| submitted_at | datetime | YES | Submission timestamp |
| reviewed_by_id | bigint | YES | FK -> User (reviewer) |
| reviewed_at | datetime | YES | Review timestamp |
| review_comments | text | YES | Review feedback |
| issued_at | datetime | YES | Issue timestamp |
| issued_by_id | bigint | YES | FK -> User (authorizer) |
| content_hash | varchar(64) | NO | SHA-256 of report payload |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: NCR
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| ncr_number | varchar(64) | NO | Controlled sequence |
| inspection_visit_id | bigint | YES | FK -> InspectionVisit |
| report_revision_id | bigint | YES | FK -> ReportRevision |
| itp_activity_id | bigint | YES | FK -> ITPActivity |
| description | text | NO | Nonconformity description |
| requirement_reference | text | YES | Relevant standard or criterion |
| evidence | jsonb | YES | Supporting photos or docs |
| severity | varchar(32) | YES | 'minor', 'major', 'critical' |
| responsible_party_id | bigint | YES | FK -> User or Vendor |
| proposed_corrective_action | text | YES | Proposed fix |
| root_cause | text | YES | Root cause analysis |
| target_completion_date | date | YES | Deadline |
| status | varchar(32) | NO | 'open', 'in_progress', 'verification', 'closed', 'waived' |
| closed_at | datetime | YES | Closure timestamp |
| closed_by_id | bigint | YES | FK -> User |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: Timesheet
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| inspector_id | bigint | NO | FK -> InspectorProfile |
| project_id | bigint | NO | FK -> Project |
| assignment_id | bigint | YES | FK -> Assignment |
| month | date | NO | First day of month |
| status | varchar(32) | NO | 'draft', 'submitted', 'approved', 'locked' |
| submitted_at | datetime | YES | Submission timestamp |
| approved_by_id | bigint | YES | FK -> User |
| approved_at | datetime | YES | Approval timestamp |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: TimesheetEntry
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| timesheet_id | bigint | NO | FK -> Timesheet |
| work_date | date | NO | Date of work |
| start_time | time | YES | Start time |
| end_time | time | YES | End time |
| break_duration | integer | YES | Break minutes |
| actual_hours | numeric(5,2) | NO | Net working hours |
| travel_hours | numeric(5,2) | YES | Travel time |
| waiting_hours | numeric(5,2) | YES | Waiting time |
| overtime_hours | numeric(5,2) | YES | Overtime |
| location | varchar(255) | YES | Work location |
| description | text | YES | Work description |
| visit_id | bigint | YES | FK -> InspectionVisit |
| created_at | datetime | NO | UTC timestamp |

## Table: RateCard
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| contract_id | bigint | NO | FK -> Contract |
| name | varchar(255) | NO | Rate card name |
| billing_model | varchar(32) | NO | 'person_day', 'fixed_visit', 'milestone', 'reimbursable' |
| currency | char(3) | NO | Rate currency |
| region | varchar(128) | YES | Geographic region |
| effective_date | date | NO | Start date |
| expiry_date | date | YES | End date (null = open-ended) |
| is_active | boolean | NO | Currently applicable |
| created_at | datetime | NO | UTC timestamp |

## Table: RateRevision
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| rate_card_id | bigint | NO | FK -> RateCard |
| revision_number | varchar(32) | NO | Revision reference |
| rate_type | varchar(64) | NO | e.g., 'person_day', 'fixed_visit_mechanical' |
| unit | varchar(32) | NO | 'day', 'visit', 'event', 'km', 'night' |
| amount | numeric(18,4) | NO | Rate amount |
| currency | char(3) | NO | Rate currency |
| min_chargeable_unit | numeric(5,2) | YES | Minimum billable |
| overtime_multiplier | numeric(5,2) | YES | Overtime factor |
| travel_multiplier | numeric(5,2) | YES | Travel factor |
| effective_date | date | NO | When rate takes effect |
| created_at | datetime | NO | UTC timestamp |

## Table: FinancialStatement
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| project_id | bigint | NO | FK -> Project |
| statement_number | varchar(64) | NO | Controlled sequence |
| period_start | date | NO | Statement start |
| period_end | date | NO | Statement end |
| currency | char(3) | NO | Statement currency |
| total_billable | numeric(18,2) | NO | Sum of approved lines |
| total_invoiced | numeric(18,2) | NO | Previously invoiced |
| current_amount | numeric(18,2) | NO | Current statement amount |
| tax_amount | numeric(18,2) | YES | Applicable tax |
| total_due | numeric(18,2) | NO | Total including tax |
| status | varchar(32) | NO | 'draft', 'approved', 'sent', 'paid', 'partial' |
| approved_by_id | bigint | YES | FK -> User |
| approved_at | datetime | YES | Approval timestamp |
| locked_at | datetime | YES | When period was locked |
| created_at | datetime | NO | UTC timestamp |
| updated_at | datetime | NO | UTC timestamp |

## Table: SignatureRecord
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| user_id | bigint | NO | FK -> User |
| document_type | varchar(64) | NO | 'report', 'timesheet', 'ncr' |
| document_id | bigint | NO | ID of the signed document |
| revision | integer | NO | Exact revision signed |
| image | varchar(1024) | NO | Signature image path |
| content_hash | varchar(64) | NO | SHA-256 of signed content |
| ip_address | varchar(45) | YES | Request IP |
| user_agent | text | YES | Browser/device info |
| signed_at | datetime | NO | UTC timestamp |

## Table: AuditEvent
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | bigint | NO | Primary key |
| user_id | bigint | YES | FK -> User (null for system events) |
| action | varchar(128) | NO | Action identifier |
| object_type | varchar(128) | NO | Model name |
| object_id | varchar(64) | NO | Primary key of affected object |
| changes | jsonb | YES | Before/after or diff payload |
| ip_address | varchar(45) | YES | Request IP |
| user_agent | text | YES | Browser/device info |
| created_at | datetime | NO | UTC timestamp |
