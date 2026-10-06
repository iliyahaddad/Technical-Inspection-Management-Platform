# Business Workflows

## 1. Client Request Submission Workflow

```mermaid
flowchart LR
    A[Draft] -->|Save| A
    A -->|Submit| B[Submitted]
    B -->|Review| C{Complete?}
    C -->|Yes| D[Accepted]
    C -->|No| E[Clarification Required]
    E -->|Client Revises| A
    D -->|Schedule| F[Ready for Scheduling]
    F -->|Generate Notification| G[Notification Issued]
```

**States:** Draft → Submitted → Under Review → Clarification Required → Accepted → Ready for Scheduling

**Actors:** Client Requester, Client Approver, Inspection Coordinator

## 2. Inspection Notification and Assignment Workflow

```mermaid
flowchart LR
    A[Accepted IRF] -->|Generate| B[Notification Draft]
    B -->|Issue| C[Notification Issued]
    C -->|Acknowledge| D[Acknowledged]
    D -->|Recommend| E[Assignment Proposed]
    E -->|Approve| F[Assignment Confirmed]
    F -->|Notify Inspector| G[Inspector Notified]
    G -->|Accept| H[Accepted]
    G -->|Decline| I[Declined]
    H -->|Schedule| J[Visit Scheduled]
```

**States:** Draft → Issued → Acknowledged → Assignment Proposed → Assignment Confirmed → Inspector Notified → Accepted / Declined → Visit Scheduled

**Actors:** Coordinator, Inspector, Vendor Representative

## 3. Inspection Visit and Report Workflow

```mermaid
flowchart LR
    A[Scheduled] -->|Arrive| B[In Progress]
    B -->|Complete| C[Completed]
    C -->|Draft Report| D[Draft]
    D -->|Submit| E[Submitted]
    E -->|Review| F{Approved?}
    F -->|Yes| G[Approved]
    F -->|No| H[Revision Required]
    H -->|Revise| D
    G -->|Authorize Signature| I[Issued]
    I -->|Immutable| J[Issued]
```

**States:** Scheduled → In Progress → Completed → Draft → Submitted → Under Review → Revision Required → Approved → Issued

**Actors:** Inspector, Reviewer, Authorizer, Client Approver

## 4. NCR and Corrective Action Workflow

```mermaid
flowchart LR
    A[Open NCR] -->|Assign| B[In Progress]
    B -->|Submit Evidence| C[Verification]
    C -->|Pass| D[Closed]
    C -->|Fail| B
    C -->|Waive| E[Waived]
```

**States:** Open → In Progress → Verification → Closed / Waived

**Actors:** Inspector, Quality Manager, Vendor

## 5. Timesheet Approval Workflow

```mermaid
flowchart LR
    A[Draft] -->|Submit| B[Submitted]
    B -->|Review| C{Approved?}
    C -->|Yes| D[Approved]
    C -->|No| E[Returned]
    E -->|Revise| A
    D -->|Lock| F[Locked]
    F -->|MTS| G[Financial Statement]
```

**States:** Draft → Submitted → Approved → Locked

**Actors:** Inspector, Coordinator, Finance Officer

## 6. Financial Statement Workflow

```mermaid
flowchart LR
    A[Locked Data] -->|Generate| B[Draft Statement]
    B -->|Review| C{Approved?}
    C -->|Yes| D[Approved]
    C -->|No| B
    D -->|Send| E[Sent to Client]
    E -->|Pay| F[Paid / Partial]
```

**States:** Draft → Approved → Sent → Paid / Partial

**Actors:** Finance Officer, Client Approver

## 7. Document Lifecycle

```mermaid
flowchart LR
    A[Uploaded] -->|Review| B[Approved]
    B -->|Supersede| C[Superseded]
    A -->|Reject| D[Rejected]
```

**States:** Uploaded → Approved → Superseded / Rejected

**Actors:** Coordinator, Technical Manager, Client

## 8. Role Dashboard Summary

| Role | Primary Dashboard |
|------|-------------------|
| System Administrator | System health, user management, audit logs |
| General Manager | Executive KPIs, project profitability, collection status |
| Technical Manager | Template library, ITP status, report quality metrics |
| Quality Manager | NCR dashboard, corrective action status, compliance metrics |
| Project Manager | Project timeline, assignments, client communications |
| Coordinator | Request queue, notifications, assignment pipeline |
| Inspector | My assignments, upcoming visits, timesheet status |
| Reviewer | Reports awaiting review, revision history |
| Client Admin | Client users, project list, request status |
| Client Requester | My requests, draft forms, document uploads |
| Client Approver | Pending approvals, issued reports |
| Vendor Rep | Acknowledgment queue, inspection schedule |
| Finance Officer | MTS, rate cards, statements, aging receivables |
| Auditor | Read-only access to all records, export capability |
