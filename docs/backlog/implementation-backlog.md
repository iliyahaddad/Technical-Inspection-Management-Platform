# Implementation Backlog

## Guiding Principles

- Each backlog item is sized for a single developer to complete in one sprint (1–2 weeks).
- Dependencies are strictly enforced; do not start a downstream item until its upstream dependency is merged and deployed.
- P0 items block all later phases. P1 items block P2 items within the same phase.
- All items must include unit tests (>85% coverage) and integration tests for happy-path API flows.

## Phase 0 — Research and Architecture (Completed)

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 0.1 | Project bootstrap | Initialize repository, Docker Compose, CI pipeline, and development environment. | P0 | None | `docker compose up` starts all services; `pytest` passes; pre-commit hooks enforce formatting. |
| 0.2 | Architecture decision record | Document ADR-001 and evaluate open-source alternatives. | P0 | None | ADR is reviewed and signed off by stakeholders; research notes archived. |
| 0.3 | Database schema baseline | Create all initial Django models, migrations, and seed data for core entities. | P0 | 0.1 | `python manage.py migrate` runs cleanly; `data-dictionary.md` is 100% aligned with generated schema. |
| 0.4 | Authentication foundation | JWT authentication, password reset, and session management. | P0 | 0.3 | `/api/auth/login` returns access/refresh tokens; password reset email flow is testable in staging. |
| 0.5 | Permission matrix implementation | Role-based access control mapped to `Permission` and `Group` models. | P0 | 0.4 | All 13 roles from `permission-matrix.md` are seedable; API rejects unauthorized requests with 403. |

## Phase 1 — Foundation

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 1.1 | User management API | CRUD for `User`, `Role`, `UserRole`; profile editing and avatar upload. | P0 | 0.5 | Users can be created, updated, and soft-deleted; role assignment triggers permission refresh. |
| 1.2 | Client and contact management | CRUD for `Client`, `ClientUser`; import from CSV. | P0 | 1.1 | Clients and their contacts are fully manageable via API and admin; import handles 5,000 rows. |
| 1.3 | Project lifecycle | CRUD for `Project`; status transitions (`draft → active → on_hold → completed → closed`). | P0 | 1.2 | Projects enforce status business rules (e.g., cannot close if open financial statements exist). |
| 1.4 | Contract and revision tracking | CRUD for `Contract`, `ContractRevision`; versioning and effective-date logic. | P0 | 1.3 | Contracts store `contract_type` enum; revisions are immutable after creation; `effective_date` logic is unit-tested. |
| 1.5 | Inspection request (IRF) workflow | Draft, submit, review, clarification, accept/reject, schedule-ready states. | P0 | 1.3 | Coordinator can accept or return with comments; client requester sees status changes in real time via WebSocket. |
| 1.6 | Request item management | Add, remove, and update `RequestItem` lines; quantity validation against `previously_inspected_qty`. | P0 | 1.5 | `requested_qty` cannot exceed `quantity - previously_inspected_qty`; API returns 422 on violation. |
| 1.7 | Review and approval engine | Generic approval workflow for `InspectionRequest`, `InspectionReport`, and `FinancialStatement`. | P0 | 1.5 | Any object implementing `Approvable` interface can be approved or rejected with audit trail in `AuditEvent`. |
| 1.8 | Audit logging | Automatic `AuditEvent` creation on every create/update/delete; immutable log. | P0 | 1.4 | Every mutating API call produces an `AuditEvent`; log cannot be modified or deleted via ORM. |
| 1.9 | Controlled numbering | Centralized sequence generator with offline-safe caching for all document numbers. | P0 | 1.3 | Sequence numbers are unique, gap-free in normal operation, and recoverable after crash. |
| 1.10 | Document management | Upload, version, and link documents to `Project`, `RequestItem`, and `ReportRevision`. | P1 | 1.2 | Files are stored in S3-compatible storage; metadata is searchable; virus scanning is implemented in Celery worker. |

## Phase 2 — Coordination

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 2.1 | Notification engine | Email, SMS, and in-app notification dispatch via Celery/Redis. | P0 | 1.5 | Users receive email and in-app notifications for status changes; template rendering supports Persian RTL. |
| 2.2 | Inspection notification (ITN) | Create, issue, acknowledge, and track `InspectionNotification` linked to IRF. | P0 | 1.5, 2.1 | Notification numbers follow controlled sequence; vendor acknowledgment updates `acknowledged_by_id` and `acknowledged_at`. |
| 2.3 | ITP management | CRUD for `ITP` and `ITPActivity`; import from Excel and PDF. | P0 | 1.3 | ITP activities hold intervention type (`H`, `W`, `SW`, `M`, `R`); hold points are enforced in the visit workflow. |
| 2.4 | Inspector profile and certification | CRUD for `InspectorProfile` and `Certificate`; expiry alerting. | P0 | 1.1 | Certificate expiry within 30 days triggers proactive notification to inspector and coordinator. |
| 2.5 | Inspector search and matching | Query inspectors by discipline, location, availability, and conflict of interest. | P0 | 2.4 | Search returns ranked results with conflict-of-interest flag; API supports geo-radius filter. |
| 2.6 | Assignment proposal and approval | Coordinator proposes assignments; manager approves; inspector accepts/declines. | P0 | 2.2, 2.5 | Assignment state machine is enforced; self-approval is blocked by permission layer. |
| 2.7 | Visit scheduling | Calendar-based scheduling with conflict detection and reminder dispatch. | P0 | 2.6 | Double-booking of the same inspector on overlapping dates is rejected; reminders fire at configurable intervals. |
| 2.8 | Route optimization (optional) | Suggest efficient inspector routes for multi-site visits on the same day. | P1 | 2.7 | Optimization reduces total travel distance by ≥15% in benchmark dataset; feature is toggleable. |
| 2.9 | Client portal notifications | Read-only portal showing inspection requests, notifications, and report status. | P1 | 1.5, 2.2 | Client users see only their own project records; RTL layout is correct. |

## Phase 3 — Inspection and Reporting

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 3.1 | Mobile inspection portal | PWA for inspectors to view assignments, capture findings, and draft reports offline. | P0 | 2.6 | Offline queue syncs when connectivity returns; reports are partially saved to IndexedDB. |
| 3.2 | Dynamic form engine | Render inspection forms from `TemplateVersion` JSON schema; support skip logic and conditional fields. | P0 | 3.1 | A technician can upload a new template version and inspectors see it immediately on next sync. |
| 3.3 | Inspection visit execution | Start, pause, resume, and complete visits; capture timestamps, instruments, and location. | P0 | 2.7 | Visit duration is computed from `actual_start` and `actual_end`; instrument calibration status is visible. |
| 3.4 | Report drafting and submission | Inspector drafts `InspectionReport` from visit data; submits for review. | P0 | 3.3 | Report content hash is computed at submission; draft save is automatic every 60 seconds. |
| 3.5 | Technical review workflow | Independent reviewer annotates report, requests revision, or approves. | P0 | 3.4 | Reviewer can add field-level comments; revision request resets status to `draft` with revision counter incremented. |
| 3.6 | Electronic signature binding | Capture signature and bind it to report revision, timestamp, and content hash. | P0 | 3.5 | `SignatureRecord` stores image, content hash, IP, and user-agent; signature is verifiable post-issuance. |
| 3.7 | NCR creation and tracking | Raise NCR from report deviation; assign severity, responsible party, and target date. | P0 | 3.5 | NCR auto-populates evidence from report deviations; status transitions follow quality workflow. |
| 3.8 | Corrective action verification | Close NCR after verification of root cause and corrective action. | P1 | 3.7 | Quality manager can waive or close NCR; closure records `closed_by_id`, `closed_at`, and final evidence. |
| 3.9 | Report issuance and distribution | Issue final report with PDF generation and client notification. | P0 | 3.6 | Issued report is tamper-evident; client receives secure download link via notification. |
| 3.10 | Report template versioning | Version `TemplateVersion` with preview, publish, and rollback. | P1 | 3.2 | Rollback is audit-logged; published templates cannot be edited, only superseded. |
| 3.11 | Inspection analytics dashboard | KPI dashboard: visits per inspector, NCR rate, average turnaround time. | P1 | 3.9 | Dashboard loads in <2 seconds for 10,000-visit dataset; filters by project, date range, and discipline. |

## Phase 4 — MTS and Finance

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 4.1 | Rate card management | CRUD for `RateCard` and `RateRevision`; effective-date logic and currency support. | P0 | 1.4 | Rate lookups return the correct revision by `effective_date`; expired rates are retained for audit. |
| 4.2 | Timesheet entry (mobile) | Inspector logs daily hours, travel, waiting, and overtime from mobile portal. | P0 | 3.1 | Timesheet entries auto-link to `Assignment` and `InspectionVisit`; duplicate day detection is enforced. |
| 4.3 | Timesheet approval workflow | Coordinator or project manager reviews and approves monthly timesheets. | P0 | 4.2 | Approved timesheets are locked; changes require a revision entry with reason. |
| 4.4 | Expense claim management | Inspector submits expense claims with receipts; finance reviews and approves. | P0 | 3.1, 4.1 | Receipts are stored in object storage; expense types are validated against `RateRevision` daily allowance. |
| 4.5 | Billing engine | Compute `FinancialStatementLine` from approved timesheets, visits, and expenses. | P0 | 4.1, 4.3, 4.4 | Engine respects contract type, allocation ratios, and double-billing safeguards. |
| 4.6 | Mixed contract safeguards | Enforce allocation ratio limits and model separation for `mixed` contracts. | P0 | 4.5 | System rejects lines that exceed model allocation; alerts are raised to finance officer. |
| 4.7 | Double-billing prevention | Unique constraint check on source documents per project per period. | P0 | 4.5 | Duplicate insertion attempt returns `DuplicateBillingError` with clear message and source reference. |
| 4.8 | Financial statement generation | Aggregate lines into `FinancialStatement`; compute totals, tax, and due amounts. | P0 | 4.5, 4.6 | Statement totals reconcile to source documents within 0.01 currency tolerance; tax rules are configurable. |
| 4.9 | Financial statement approval | Manager approval with lock; void capability with audit trail. | P0 | 4.8 | Locked statements cannot be modified unless a `ContractRevision` or adjustment memo is issued. |
| 4.10 | Invoice generation | Create `Invoice` from approved `FinancialStatement`; send to client. | P0 | 4.9 | Invoice numbers follow controlled sequence; PDF is generated and attached to client portal notification. |
| 4.11 | Payment recording and reconciliation | Record `Payment` against `Invoice`; update statement status. | P0 | 4.10 | Partial payments set statement status to `partial`; overpayments create credit memo. |
| 4.12 | Cost ledger | Track direct project cost per timesheet entry and expense for gross profit calculation. | P0 | 4.3, 4.4 | Cost ledger reconciles to general ledger export; negative gross profit triggers alert. |
| 4.13 | Financial dashboards | Revenue, cost, margin, AR aging, and collection dashboards. | P1 | 4.8, 4.10, 4.12 | Dashboards refresh every 15 minutes via Celery beat; export to PDF/Excel/CSV is supported. |
| 4.14 | Multi-currency support | Exchange rate import and automatic conversion for cost and revenue reporting. | P1 | 4.8 | Exchange rates are sourced from configurable providers; conversions are logged with source and effective date. |
| 4.15 | Revenue recognition | Apply percentage-of-completion or milestone-based recognition rules. | P1 | 4.8, 4.10 | Recognized revenue updates automatically when milestones are issued or reports are approved. |

## Phase 5 — Commercial Readiness

| ID | Title | Description | Priority | Dependencies | Acceptance Criteria |
|----|-------|-------------|----------|--------------|---------------------|
| 5.1 | Security hardening | Penetration testing, CSP headers, rate limiting, secrets rotation, and dependency audit. | P0 | 1–4 | OWASP ZAP scan passes with no high-severity findings; secrets are stored in Vault or environment variables. |
| 5.2 | Performance optimization | Database indexing, query optimization, caching strategy, and load testing. | P0 | 1–4 | API p95 latency < 300ms for 500 concurrent users; dashboard queries use `EXPLAIN ANALYZE` to verify index usage. |
| 5.3 | Backup and disaster recovery | Automated PostgreSQL backups, point-in-time recovery, and runbook documentation. | P0 | 5.2 | Restore from backup completes in < 1 hour; RPO ≤ 15 minutes, RTO ≤ 2 hours. |
| 5.4 | UAT execution | End-to-end user acceptance testing with client representatives and inspectors. | P0 | 1–4 | UAT sign-off document is produced; critical bugs are resolved before deployment. |
| 5.5 | Deployment pipeline | Production Docker Compose, blue-green or rolling deployment, and health checks. | P0 | 5.3 | Zero-downtime deployment is demonstrated in staging; health checks return 200 before traffic is routed. |
| 5.6 | Monitoring and alerting | Prometheus/Grafana dashboards, Sentry error tracking, and PagerDuty integration. | P1 | 5.5 | Alerts fire within 5 minutes of incident; on-call rotation is documented. |
| 5.7 | Data migration tooling | Scripts to import legacy client data and validate referential integrity. | P1 | 5.4 | Migration dry-run produces validation report; zero data loss on production cutover. |
| 5.8 | Training materials | Video tutorials, quick-reference cards, and admin handbook in Persian and English. | P1 | 5.4 | Training materials are reviewed by a native Persian speaker; completion rate ≥ 80% in first month. |
| 5.9 | License compliance audit | Verify all third-party libraries comply with proprietary commercial use. | P0 | 0.2 | Legal team signs off; no GPLv3 dependencies in production Docker image. |
| 5.10 | Go-live checklist and rollback plan | Final checklist, cutover schedule, and rollback triggers. | P0 | 5.1–5.9 | Rollback is tested in staging; all stakeholders approve go-live checklist. |
