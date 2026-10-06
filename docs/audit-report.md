# Project review and remediation report

Review date: 2026-10-04

## Fixed in this revision

1. **Development frontend container was misconfigured.** Compose was building the production Nginx image while trying to expose Vite on port 5173. The frontend Dockerfile now has a `dev` target, and development Compose runs Vite. The Vite API proxy target uses the `backend` service hostname in Docker.
2. **Frontend image could not build.** The Dockerfile copied `frontend/nginx.conf`, which did not exist. Added a production Nginx config with SPA fallback, health endpoint, asset caching, upload size limit, and basic security headers.
3. **Production Compose was inconsistent with the repository.** It referenced `config.settings_production` before that module existed, used incompatible database variable names and incorrect build contexts/paths, contained weak default credentials, and exposed monitoring services by default. Replaced it with a minimal production stack, required secrets, private internal network, health checks, and explicit persistent volumes.
4. **Production settings were missing.** Added `settings_production.py` with required secret/host/database validation, PostgreSQL URL parsing, secure cookie/security defaults, API throttling, and container-friendly logging. TLS termination must be configured at a trusted reverse proxy; see deployment runbook.
5. **Backend dependencies were incomplete.** Added `gunicorn` (used by the container command) and `drf-spectacular-sidecar` (referenced by Django settings).
6. **Logging could prevent startup.** Removed the mandatory file handler whose parent directory was not guaranteed to exist in the backend image; container logs now go to stdout/stderr. Static asset directories are only registered when present.
7. **User API had unsafe defaults.** Ordinary users could query the full user directory, and public user creation was always enabled. User listing/deletion is now staff-only, regular users are scoped to their own profile, `is_active` is read-only in the API, and public registration is disabled unless explicitly enabled by configuration.
8. **Project setup and operations were under-documented.** Added environment template, secret-generation helper, offline preflight checker, and this report.

## Important findings that still require a deliberate production decision

- **Initial migrations are missing for most custom Django apps.** No initial migrations were present for most custom apps. Startup has been changed to `migrate --noinput` (without `--run-syncdb`) and will require reviewed, version-controlled initial migrations. Run `scripts/generate_migrations.sh` in an environment with Django dependencies installed, review and commit the generated files, then test clean installs and upgrades before deployment.
- **Role-based/object-level authorization is not implemented to the level described in `docs/workflows/permission-matrix.md`.** Several API viewsets currently use only `IsAuthenticated`, which is not sufficient to isolate clients, projects, vendor records, inspector compensation, or financial data. Do not expose the application to untrusted users until role permissions and queryset-level tenant/object filtering have been implemented and tested. The account API hardening above is only a partial correction.
- **TLS must be supplied by a trusted reverse proxy.** The included production Nginx is an HTTP reverse proxy and does not provision certificates. Put it behind a TLS terminator, preserve a trusted `X-Forwarded-Proto` header, set `SECURE_SSL_REDIRECT=true`, and configure `CSRF_TRUSTED_ORIGINS` with the HTTPS origin. Do not expose a plain-HTTP deployment to the public internet.
- **The backend is pinned to Django 5.1.7, which should be upgraded to a currently supported LTS/security release after compatibility testing before go-live.**
- **Build and integration tests could not be executed in this environment.** Django is not installed in the execution environment and package-index DNS/network access failed. The static preflight and syntax/config checks are not proof that database migrations, API behavior, or the browser build pass. Run the full test plan below on a machine with Docker and package access.
- **Frontend lint/format tooling was inconsistent.** The `lint` script now performs the TypeScript project check; formatting has no script until a formatter is added to both package manifest and lockfile.

## Release test plan

1. `python scripts/preflight.py`
2. `docker compose config` and `docker compose -f docker-compose.production.yml config`
3. `docker compose up --build` on a clean development database; verify `/api/health/`, login, project/client CRUD, uploads, reports, and task processing.
4. In backend container: `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `pytest --cov=apps --cov-report=term-missing`.
5. In frontend container: `npm ci`, `npm run lint`, `npm run build`.
6. Test permission boundaries with at least two clients, two vendors, two inspectors, an auditor, and a finance user; verify both list endpoints and direct object IDs.
7. Test backup restore, media-file access controls, email delivery, Celery retries, audit trail integrity, database upgrade/rollback, and disaster recovery.
8. Before go-live, complete TLS, secret rotation, backups, alerting, log retention, vulnerability scanning, and a documented incident-response plan.
