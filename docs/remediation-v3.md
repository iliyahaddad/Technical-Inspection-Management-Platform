# Remediation pass v3 (2026-10-05)

## Which codebase to continue with
The GitHub repository (`iliyahaddad/Technical-Inspection-Management-Platform`) contains **2 commits** and a README
that still says "Phase 0 — Research and Architecture". The ZIP is the complete, later codebase (9 Django apps, 17 React
pages, CI, production Compose, runbooks). **Continue with the ZIP**; this tree is its successor. Push it to the repo
(`git add -A && git commit` on `main`) so the repository stops being a stub.

## Defects fixed in this pass (found by reading the code, not by running it)
| Area | Defect | Fix |
|---|---|---|
| Backend | `AuditLogMiddleware.process_response(self, request, response, callback)` had an extra argument -> **every request raised TypeError** | rewritten as a standard middleware |
| Backend | `config/__init__.py` empty -> Celery app never loaded; `.delay()` used a default broker | loads `celery_app` |
| Backend | Beat tasks pointed to `check_ncr_overdue` in the wrong module; `timedelta`/`NCR` missing imports | tasks moved/fixed in `apps/reports/tasks.py`, `apps/inspections/tasks.py` |
| Backend | Notification e-mails passed lazy translation objects to Celery (JSON) -> always failed; all `notify_*` helpers were never called | plain strings, in-app + e-mail via `transaction.on_commit`, wired into assignment/report/NCR flows |
| Backend | Audit trail never recorded the user (thread-local never read), diffed nothing on update, was disabled on every DB error, leaked values | `pre_save` snapshot diff, request user/IP, secret redaction, append-only model/admin, access limited to auditor/GM/quality |
| Backend | Pagination (`{count,results}`) vs frontend arrays; frontend called `/api/projects/` (real route `/api/projects/projects/`) | frontend follows pages; URLs corrected (all 15 frontend endpoints now cross-checked against the routers) |
| Backend | Review endpoint payload mismatch (`decision: accept` vs frontend `action: accepted`) | accepts both; comment required for reject/clarification; cannot re-review |
| Backend | Submitted/approved/issued records were editable through plain PUT/PATCH/DELETE | `LockedStatusMixin` (409), child rows locked with parent |
| Backend | Two concurrent approvals could both pass | `select_for_update` in `TransitionMixin`; `ATOMIC_REQUESTS=True` |
| Backend | Preparer could approve their own report/timesheet/expense | separation-of-duties check |
| Backend | Report `content_hash` was hash of `str(FK)` values (meaningless) | real digest at submit; re-verified at approve/issue (409 on tamper) |
| Backend | Upload fields were `CharField` paths; extension-only validation; public cache of media | real `FileField`s, magic-byte validator, authorised downloads via `X-Accel-Redirect`, `no-store` |
| Backend | PDF: no Arabic shaping/bidi, no XML escaping (user text parsed as markup), mislabelled fields, findings always empty, `TA_RIGHT` table crash | shaping, escaping, real findings (checklist, measurements, NCRs), font discovery, tested render |
| Backend | `DEBUG` defaulted to True; weak secret fallback; no login throttle | secure default, mandatory `SECRET_KEY`, scoped login throttle, logout with refresh blacklist |
| Backend | Unused heavy dependencies (weasyprint, pydantic, bcrypt, dotenv, phonenumbers); Django 5.1 | removed; Django 5.2 LTS range |
| Frontend | Auth: three inconsistent implementations, hard-coded fake user `user@example.com`, role menu used role names that don't exist in the backend, no refresh-token use | one token store, refresh on 401, real `/accounts/me/` roles, route guards |
| Frontend | i18n loaded asynchronously on every render (keys shown instead of text) | static load, fallback to English |
| Frontend | Dashboard NCR/inspector counts hard-coded to 0 | real counts, per-widget fault tolerance |
| Ops | Nginx duplicates (`deploy/nginx` with wrong upstreams); no rate limits; no readiness probe; no backup job; root user in image | consolidated, rate limits, `/api/health/ready/`, `backup` profile, non-root image |

## NOT done / cannot be verified here (be explicit)
This environment had **no network and no Django install**, so nothing below was executed:
1. **Initial migrations are still missing** for 9 apps. Run once: `sh scripts/generate_migrations.sh`, review, commit. Two models changed field types (`CharField` -> `FileField`/`TextField`); on a fresh DB this is irrelevant.
2. Backend test suite (`pytest`) has **not been run**. Legacy tests were given role fixtures; expect some to need small adjustments. New tests: `backend/tests_hardening.py`.
3. `npm ci && npm run build` has **not been run**; TypeScript errors are possible.
4. Dependency versions I changed (Django 5.2, celery-beat 2.8, arabic-reshaper, python-bidi) were not installed.
5. Pages are still thin CRUD tables (no detail screens, filters, file upload UI, PDF buttons). Backend endpoints for these exist.

## Suggested next steps (priority order)
1. Generate/commit migrations -> run CI -> fix failures.
2. Request detail page + report editor (checklist/measurements/attachments) + PDF/download buttons.
3. TOTP 2FA for internal roles (`django-otp` is installed, not enforced).
4. Malware scan of uploads (ClamAV sidecar), S3 private bucket, retention policy.
5. Metrics (`django-prometheus`) — `deploy/monitoring/prometheus.yml` expects `/metrics`, which does not exist yet.
6. Server-side pagination in UI instead of loading all pages.
