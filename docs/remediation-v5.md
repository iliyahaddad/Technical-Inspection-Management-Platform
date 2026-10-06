# Remediation v5 (review of the uploaded v4)

## Defects found in v4 and fixed
| Area | Problem in v4 | Fix |
|---|---|---|
| Frontend | `ReportsPage.tsx` was a minified one-liner with a **syntax error** (`]])`) and undefined `file` state -> the whole app failed to build | rewritten readably; blank decimals sent as `null`; PATCH instead of PUT; locked-report banner; upload only when allowed |
| Frontend | PDF button used a plain URL (no `Authorization` header -> 401) | fetched as blob, opened in a new tab |
| Frontend | Pagination opt-out via custom `X-Keep-Pagination` header (sent to the server, CORS-visible) | typed axios config flag `keepPagination` |
| Frontend | Request detail / 2FA pages hard-coded English, showed project id, 2FA page showed no provisioning URI | translated, project name, secret + URI, "mandatory" notice; login redirects to 2FA setup when required |
| Backend | `PAGE_SIZE_QUERY_PARAM` / `MAX_PAGE_SIZE` in `REST_FRAMEWORK` are **ignored by DRF**: `?page_size=` never worked | `config.pagination.StandardPagination` |
| Backend | 2FA enforced only at login *if a device already existed*; users could skip enrolment, and disable it again | mandatory roles are blocked (403) by `RoleAndScopePermission` until enrolled; enrolled users are always challenged; mandatory users cannot disable; setup/verify/disable are throttled; stale unconfirmed secrets replaced |
| Backend | 2FA role list duplicated in two files and out of sync with the access matrix | single `INTERNAL_2FA_ROLES` / `needs_2fa()` in `config/access_control.py` |
| Backend | `/metrics/` was **public**, the counter measured nothing but its own scrapes, `/celery-metrics/` returned Django metrics | bearer-token protected (closed if `METRICS_TOKEN` empty and not DEBUG), real per-route request/latency metrics via middleware, alias removed, Prometheus config uses `credentials_file` |
| Backend | Malware scan also ran on already-stored files (admin edits) and ClamAV (~1 GB RAM) was a *hard* dependency of backend startup | scan only new uploads; ClamAV behind compose profile `scan` |
| Backend | Report revisions, checklist answers, measurements and attachments stayed editable after the report was submitted/approved (defeated the content digest) | `ReportChildLockMixin` (409) |
| Repo | `node_modules/` shipped as 1 MB of empty directories, `__pycache__` (cp313) everywhere | removed |

## Still NOT verified (no Django/Node packages, no Docker in this environment)
* `makemigrations` has never been run: **9 apps still have no migration files** (only `audit` has one). Run `sh scripts/generate_migrations.sh`.
* `pytest`, `npm ci && npm run build` not executed. Done instead: Python byte-compilation of all files, YAML parsing of compose/Prometheus files, TypeScript *syntax* check of all 60+ source files (0 errors), cross-check of every frontend endpoint against the backend routers. Type errors / import errors can still exist.
* Version pins `prometheus-client==0.21.1`, `clamd==1.0.2` taken from v4 unverified.

## Release gate (unchanged)
```bash
sh scripts/generate_migrations.sh
cd backend && pytest -q
cd ../frontend && npm ci && npm run build
```
