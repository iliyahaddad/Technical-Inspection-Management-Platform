# Finalization / Remediation v4

## Implemented in this build

1. Internal-role TOTP 2FA endpoints and production login enforcement hook.
2. Optional fail-closed ClamAV malware scanning for all upload validators that use the shared validator.
3. Prometheus `/metrics/` endpoint and `/celery-metrics/` compatibility endpoint.
4. Configurable server-side API pagination (`API_PAGE_SIZE`, `API_MAX_PAGE_SIZE`).
5. Inspection Request detail page and workflow submit action.
6. Inspection Report editor with quantities, narrative, deviations and recommendations.
7. Report attachment upload UI and PDF action.
8. Server-side pagination UI for Inspection Requests and Inspection Reports.
9. Automatic first `ReportRevision` creation when an inspection report is created.
10. Docker Compose security wiring for ClamAV.
11. Added finalization documentation and security test scaffolding.

## Validation status

Static Python compilation and YAML/JSON structural validation were completed in the build environment.

Full Django integration tests and frontend production build could not be executed in this environment because Docker is unavailable and third-party Python packages are not installed locally. The project therefore retains the CI commands for authoritative execution.

## Required release gate

Before declaring the release production-ready, run:

```bash
sh scripts/generate_migrations.sh
cd backend && pytest -q
cd ../frontend && npm ci && npm run build && npm run lint
```

The migration command must generate and review the initial migrations for all application apps and commit them. The existing CI workflow already enforces `makemigrations --check --dry-run` before tests.
