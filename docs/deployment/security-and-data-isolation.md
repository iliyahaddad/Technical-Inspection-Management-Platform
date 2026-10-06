# Security, tenant isolation, migrations and production operations

## Access-control model

- Assign role keys as Django Group names, matching `backend/apps/accounts/roles.py` (for example `inspector`, `client_requester`, `finance_officer`). A role submitted by a client is never trusted.
- Superusers/staff and `sys_admin` are global operators. Client roles are scoped to `ClientUser` links. Inspectors are scoped to their own profile, assignments, visits, reports and timesheets. Project managers are scoped to projects they manage. Unmapped resources fail closed.
- `VendorUser` now links vendor representatives to vendors and is manageable in Django admin. Vendor representatives are scoped to linked vendors and purchase orders/projects associated with those vendors. `Document` and `DocumentVersion` now have client/project/vendor ownership, uploader, version metadata and checksums; downloads pass through an authenticated, scoped endpoint. Validate retention, malware scanning and private object storage before accepting untrusted uploads in production.
- Before enabling any new API endpoint, add its model to `config/access_control.py`, add object/foreign-key scope tests, and confirm serializer actor/workflow fields are read-only. Do not expose a raw unscoped `Model.objects.all()` in a view or custom action.
- Create role groups with `python scripts/bootstrap_roles.py` after migrations, or through Django admin; this command does not assign users. Review least privilege before assigning each user. Do not grant staff/superuser as a substitute for a business role.

## Versioned migrations (required before production)

This repository snapshot had no initial migrations for accounts, clients, projects, inspections, notifications, reports, mts and documents. Django and its dependencies are not bundled in the repository. In an environment with `backend/requirements/base.txt` installed, run:

```sh
scripts/generate_migrations.sh
```

Review the generated `0001_initial.py` files, commit them to source control, then run `python manage.py makemigrations --check --dry-run` and `python manage.py migrate --plan`. Run migrations against a disposable copy of the target database first and verify rollback/restore. Production startup uses `migrate --noinput` only; it must not use `--run-syncdb`.

**Do not deploy until those generated migration files are committed.** The execution environment used to prepare this patch had no Django installation and no package-network access, so migration files could not safely be generated or validated here. `scripts/preflight.py` reports this as a blocking issue.

## TLS and secrets

- Terminate TLS at a trusted reverse proxy/load balancer; expose this stack's HTTP port only on loopback/private networking. Set `SECURE_SSL_REDIRECT=true`, `CSRF_TRUSTED_ORIGINS=https://...`, and the exact `ALLOWED_HOSTS`.
- The proxy must overwrite, not append untrusted client values to, `X-Forwarded-Proto` and must be the only route to Nginx. Never expose the Django/Gunicorn or PostgreSQL ports publicly.
- Generate `SECRET_KEY` with `scripts/generate_secret.py`. Store `.env` in a secret manager or protected host file with restrictive permissions; never commit it. Rotate DB/email/JWT signing secrets under a documented maintenance plan, with staged rollout and invalidation of old tokens where required.
- Enable database TLS (`DB_SSL_REQUIRE=true`) when PostgreSQL is remote; configure certificate validation (`verify-full` with a CA) for production remote DBs rather than trusting any server certificate.
- HSTS is enabled when HTTPS redirect is enabled. Enable preload only after all subdomains are HTTPS-ready.

## Backup, restore and observability

- Run encrypted off-host backups on a schedule; define retention (for example daily/weekly/monthly) and alert on failed or stale backups. Back up uploaded media/object storage as well as PostgreSQL.
- The restore script requires `CONFIRM_RESTORE=YES`; restore to a disposable database first and validate row counts, migrations and a sample PDF/report before a production recovery.
- Regularly run a restore drill and document RPO/RTO. Restrict backup directory permissions and never place credentials in command-line arguments or logs.
- Send structured application/proxy logs to centralized storage with retention and access controls. Alert on repeated 401/403, 5xx, database/Redis health failures, disk pressure, backup failures and unusual privileged changes. Redact credentials, tokens and personal data from logs.

## Go-live blocking checklist

- [ ] Versioned initial migrations committed and applied to a clean PostgreSQL database.
- [ ] Cross-tenant tests for every API resource and every custom action.
- [ ] FK injection tests (including serializer aliases such as `client_id`) pass.
- [ ] VendorUser membership is populated and reviewed; document uploads are backed by private storage, malware scanning and retention controls.
- [ ] TLS externally verified; backend/database not publicly reachable.
- [ ] Backup + media restore drill passes; retention and alerting active.
- [ ] Django deployment checks, dependency/security scan and full API test suite pass.
