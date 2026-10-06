# Permission Matrix

## Roles and Capabilities

| Role | Key | Description |
|------|-----|-------------|
| System Administrator | `sys_admin` | Full system access, configuration, user management |
| Company General Manager | `gm` | Executive dashboards, financial overview, approval authority |
| Technical Manager | `tech_manager` | Template design, standard management, technical review |
| Quality Manager | `quality_manager` | NCR oversight, process compliance, report approval |
| Project Manager | `project_manager` | Project dashboards, assignment oversight, client liaison |
| Inspection Coordinator | `coordinator` | Request review, notification creation, inspector assignment |
| Inspector | `inspector` | Mobile inspection, timesheets, expense claims, report drafting |
| Independent Report Reviewer | `reviewer` | Technical review of inspection reports |
| Client Administrator | `client_admin` | Client user management, portal administration |
| Client Requester | `client_requester` | Submit inspection requests, upload documents |
| Client Approver | `client_approver` | Approve inspection requests, review reports |
| Vendor Representative | `vendor_rep` | Acknowledge notifications, limited project visibility |
| Finance Officer | `finance_officer` | MTS access, rate management, statement generation |
| Read-Only Auditor | `auditor` | Read-only access to all records for compliance |

## Permission Details

### Company Administrator (`sys_admin`)
- Full CRUD on all master data
- User and role management
- System configuration
- Database backup and restore
- Audit log access
- No restriction on object-level access

### General Manager (`gm`)
- Read all projects, clients, and financials
- Approve high-value contracts and change orders
- Access management dashboards
- Cannot modify master data without admin role

### Technical Manager (`tech_manager`)
- Create and version inspection templates
- Manage ITPs, standards, and disciplines
- Review and approve technical report content
- Access instrument calibration records
- Cannot approve financial transactions

### Quality Manager (`quality_manager`)
- Review and approve NCRs and corrective actions
- Override release notes when authorized
- Access quality dashboards
- Cannot modify inspection results

### Project Manager (`project_manager`)
- View assigned projects
- Monitor assignment and visit status
- Communicate with clients
- Cannot access other projects' financials

### Inspection Coordinator (`coordinator`)
- Review and return inspection requests
- Create inspection notifications
- Recommend inspector assignments
- Cannot approve own assignments
- Cannot issue final reports

### Inspector (`inspector`)
- View own assignments and visits
- Complete inspection forms
- Submit timesheets and expenses
- Draft inspection reports
- Cannot approve own reports
- Cannot view other inspectors' compensation

### Independent Report Reviewer (`reviewer`)
- Review assigned reports
- Return reports with field-level comments
- Cannot modify report data
- Cannot approve timesheets

### Client Administrator (`client_admin`)
- Manage client users
- View client's projects and requests
- Cannot access other clients' data

### Client Requester (`client_requester`)
- Create draft inspection requests
- Submit requests
- Upload supporting documents
- View own request status
- Cannot access other clients' data

### Client Approver (`client_approver`)
- Approve or reject inspection requests
- Review issued reports
- Cannot modify request data after submission

### Vendor Representative (`vendor_rep`)
- Acknowledge inspection notifications
- Upload vendor documents
- View assigned inspections
- Cannot access other vendors' data

### Finance Officer (`finance_officer`)
- Access MTS and financial statements
- Manage rate cards and contract pricing
- Generate invoices and statements
- Cannot modify inspection results
- Cannot access raw inspector compensation without authorization

### Read-Only Auditor (`auditor`)
- Read all records
- Export data for compliance
- Cannot modify, create, or delete
- Cannot access secret keys or credentials

## Object-Level Permission Rules

1. **Client Data:** Users can only access records where the client matches their assigned client (or they hold a company role).
2. **Project Data:** Users can only access records within projects they are authorized for.
3. **Inspector Data:** Inspectors see only their own assignments, timesheets, and reports. Coordinators see all within their projects.
4. **Financial Data:** Financial details are visible only to finance officers and general managers. Inspectors and clients see only their own billing-relevant summaries.
5. **Signature Data:** Signatures are visible to authorized signers and auditors only.
6. **Document Access:** Enforced at the API and storage layer; URLs are not guessable.

## Multi-Role Behavior

When a user holds multiple roles, the union of permissions applies. For approval workflows, the system must prevent a single user from both creating and approving the same record unless explicitly configured.

## API Enforcement

All permission checks occur in Django view permissions, DRF permission classes, and queryset filters. Frontend UI hiding is cosmetic only and does not constitute authorization.
