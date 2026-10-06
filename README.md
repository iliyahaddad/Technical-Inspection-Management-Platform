# Technical Inspection Management Platform

A Persian-first web application for technical inspection operations: clients, projects, inspection requests, assignments, site visits, reports, non-conformities, release notes, inspector timesheets, expenses, and financial statements.

## Technology

- **Backend:** Django 5.2, Django REST Framework, PostgreSQL, Redis, Celery
- **Frontend:** React 18, TypeScript, Vite, TanStack Query, MUI
- **Operations:** Docker Compose, Nginx, health checks, persistent database/media volumes

## Quick start — development

Requirements: Docker Engine and Docker Compose v2.

```bash
# From the repository root
docker compose up --build
```

- Frontend: http://localhost:5173
- API health: http://localhost:8000/api/health/
- API schema: http://localhost:8000/api/schema/
- Django admin: http://localhost:8000/admin/

Create the first administrator after the services are healthy:

```bash
docker compose exec backend python manage.py createsuperuser
```

The development database and Redis use local-only ports. Default development credentials are for local use only; never reuse them in production.

## Production deployment

1. Copy `.env.production.example` to `.env` and replace all placeholders. Generate a Django secret with `python scripts/generate_secret.py`. Use a long random database password and do not commit `.env`.
2. Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, SMTP values, and the public HTTPS domain.
3. Place the bundled HTTP Nginx reverse proxy behind a trusted TLS terminator. Ensure the proxy forwards `X-Forwarded-Proto` correctly; then set `SECURE_SSL_REDIRECT=true`. Do not expose plain HTTP directly to the public internet.
4. Validate configuration: `python scripts/preflight.py`, `docker compose -f docker-compose.production.yml config`.
5. Start: `docker compose -f docker-compose.production.yml up --build -d`.
6. Create the first administrator: `docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser`.
7. Configure encrypted off-host backups, restore tests, monitoring/alerting, secret rotation, and log retention before go-live.

## Quality status and known limitations

The application source is a work in progress, not yet certified for production use. Review `docs/audit-report.md` before deploying. In particular, role/object-level authorization has been added as a default-deny tenant-scoping layer, but it still requires full integration/security testing. **First step on a new machine:** run `sh scripts/generate_migrations.sh` (uses Docker), review and commit `backend/apps/*/migrations`. Then `docker compose up --build`. See `docs/remediation-v3.md` for what changed and what is still unverified. See `docs/deployment/security-and-data-isolation.md`.

## Documentation

- `docs/architecture/` — architecture decisions
- `docs/database/` — data dictionary and ER diagram
- `docs/workflows/` — workflows and permission matrix
- `docs/mts/` — financial calculation specification
- `docs/deployment/` — go-live checklist
- `docs/audit-report.md` — first remediation report
- `docs/remediation-v5.md` — review of v4: fixes and verification status
- `docs/remediation-v3.md` — latest fixes, honest verification status, next steps

## License

Proprietary — commercial use only.

## Production hardening added in finalization

The platform now includes:

- Optional internal-role TOTP 2FA with setup, verification and disable endpoints.
- Optional fail-closed ClamAV malware scanning for validated uploads.
- Prometheus-compatible `/metrics/` endpoint plus `/celery-metrics/` compatibility endpoint.
- Configurable DRF server-side page size (`API_PAGE_SIZE`, `API_MAX_PAGE_SIZE`).
- Inspection request detail workflow UI.
- Inspection report editor, attachment upload and PDF actions in the frontend.
- Server-side pagination UI for inspection reports.
- Automatic initial report revision creation for new inspection reports.
- Production/development Compose wiring for ClamAV.

### Required final validation in a Docker-enabled environment

Run:

```bash
sh scripts/generate_migrations.sh
cd backend && pytest -q
cd ../frontend && npm ci && npm run build && npm run lint
```

The repository intentionally does not claim those commands were executed in this build environment when Docker/Python third-party packages are unavailable.
