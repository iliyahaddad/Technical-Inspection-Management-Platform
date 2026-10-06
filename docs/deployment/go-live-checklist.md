# Go-Live Checklist and Rollback Plan

## Go-Live Checklist

### Pre-Deployment
- [ ] Full backend/frontend test suites pass in CI (do not rely on historic test counts)
- [ ] `python scripts/preflight.py` passes, including versioned migrations
- [ ] License audit passes with no prohibited licenses (`python scripts/license_audit.py`)
- [ ] SECRET_KEY is set to a strong random value in production environment
- [ ] DEBUG is set to `False` in production environment
- [ ] ALLOWED_HOSTS is configured with production domains only
- [ ] PostgreSQL database is provisioned and accessible
- [ ] Redis is provisioned and accessible
- [ ] S3/compatible object storage is configured for media and documents
- [ ] SMTP email backend is configured
- [ ] TLS is terminated by a trusted reverse proxy; app port is private and forwarded-proto headers are overwritten by that proxy
- [ ] HTTPS certificates are installed and SECURE_SSL_REDIRECT is True
- [ ] Database and media backups are scheduled, encrypted, off-host, and restore-tested
- [ ] Celery workers and beat scheduler are configured
- [ ] Docker images are built and tagged with version

### Security Hardening
- [ ] OWASP ZAP scan passes with no high-severity findings
- [ ] CSP headers are configured
- [ ] Rate limiting is enabled (if using django-ratelimit or similar)
- [ ] Password policy enforces minimum 12 characters
- [ ] JWT tokens have appropriate lifetimes (60 min access, 7 day refresh)
- [ ] CORS is restricted to production frontend origin
- [ ] Admin panel is protected with IP allowlist or 2FA
- [ ] Secrets are stored in a secret manager or protected environment file, not in code; rotation procedure is documented
- [ ] Vendor-user relationships and document ownership are implemented before those APIs are enabled

### Data Migration
- [ ] Legacy data migration scripts are tested in staging
- [ ] Versioned initial migrations exist for every custom app; `makemigrations --check --dry-run` passes
- [ ] Referential integrity is validated
- [ ] Cross-tenant API tests and foreign-key injection tests pass for every resource/action
- [ ] Migration dry-run produces validation report with zero errors

### Monitoring
- [ ] Prometheus/Grafana dashboards are deployed
- [ ] Sentry error tracking is configured
- [ ] Health check endpoint (`/api/health/`) returns 200
- [ ] Log aggregation is configured

### UAT
- [ ] UAT sign-off document is produced
- [ ] Critical bugs are resolved before deployment

### Deployment
- [ ] Blue-green or rolling deployment pipeline is tested in staging
- [ ] Rollback procedure is documented and tested
- [ ] Deployment window is communicated to stakeholders
- [ ] On-call team is available during deployment

## Rollback Plan

### Trigger Conditions
Rollback is triggered if:
- API p95 latency exceeds 1000ms for 5 minutes
- Error rate exceeds 5% for 5 minutes
- Database connection failures exceed 10% of requests
- Any P0 functionality is completely unavailable

### Rollback Procedure
1. Immediately redirect traffic to previous stable Docker image
2. Restore database from last known good backup (if data corruption suspected)
3. Verify health check endpoint returns 200
4. Communicate status to stakeholders within 15 minutes
5. Preserve logs and metrics for post-incident review

### Rollback Timeline
- Detection: 0-5 minutes
- Decision: 5-10 minutes
- Execution: 10-15 minutes
- Verification: 15-20 minutes

### Contact List
- Technical Lead: [Name/Contact]
- DevOps: [Name/Contact]
- QA Lead: [Name/Contact]
- Client Success: [Name/Contact]
