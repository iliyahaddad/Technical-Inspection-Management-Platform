# Remediation v6 — Review of technical-inspection-final-v5

## Confirmed fixes in this pass

| Area | Defect | Resolution |
|---|---|---|
| Reports | Creating a report could fail because `content_hash` is required by the model but was not supplied during serializer save | Initial report creation now explicitly stores an empty digest and creates the first immutable revision snapshot |
| Reports | A report returned for revision remained in `revision_required`, while the submit endpoint accepted only `draft` | Editing a returned report transitions it back to `draft`, clears prior review metadata, increments the revision and creates a new revision snapshot |
| Reports | Editing a draft report changed header/body fields without updating its `ReportRevision` snapshot | The latest revision snapshot is synchronized on draft edits |
| Notifications | Submission notification targeted `reviewed_by`, which is empty at submission time | Notification now falls back to the inspection assignment proposer/coordinator |
| Attachments | Attachment metadata could remain incomplete | Upload stores original filename, file size and content type from the validated upload |
| Frontend PDF | Blob URL was left allocated indefinitely | Object URL is revoked after use; popup blocking produces an explicit error |
| Documentation | README reported Django 5.1 while requirements pin Django 5.2 | README corrected to Django 5.2 |

## Verification performed in this environment

- Python source compilation: PASS
- YAML parsing for Compose, production Compose, CI and Prometheus: PASS
- Static preflight: PASS except for the intentionally blocking missing migration set
- Frontend build: attempted, but the supplied `node_modules` was incomplete and the environment could not reach npm registry to reinstall dependencies
- Django/pytest: cannot execute because Django and backend dependencies are not installed and external package download is unavailable
- Docker: unavailable in this execution environment

## Remaining release blocker

Eight application packages still have no committed migration files:

`accounts`, `clients`, `projects`, `inspections`, `notifications`, `reports`, `mts`, `documents`.

Only `audit` currently contains an initial migration.

The canonical command remains:

```bash
sh scripts/generate_migrations.sh
```

After migrations are generated and reviewed, the release gate is:

```bash
cd backend && pytest -q
cd ../frontend && npm ci && npm run build && npm run lint
```

## Review of v6 (follow-up pass)
* Checked every v6 change against the models/serializers (`proposed_by`, `revision`, read-only fields): consistent.
* Small fix: syncing the draft snapshot no longer overwrites the revision's original `created_by`.
* Added `backend/tests_report_flow.py` covering create -> edit -> submit -> locked -> self-approval blocked -> return -> edit (revision 2) -> resubmit -> approve. **Not executed** (no Django here); field names in its fixtures may need a small adjustment.
* Still open: migrations for 8 apps (`sh scripts/generate_migrations.sh`), then `pytest -q` and `npm ci && npm run build`.
