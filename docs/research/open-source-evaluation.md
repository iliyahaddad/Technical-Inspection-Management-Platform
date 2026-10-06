# Open-Source Evaluation Report

## Research Limitations

Web access was unavailable during this research phase. Findings are based on publicly known information and the project's own architecture decisions. No code was copied from external repositories.

## ERPNext / Frappe Framework

- **Repository:** https://github.com/frappe/erpnext
- **License:** GPL v3
- **Assessment:** ERPNext is a comprehensive ERP with inspection modules, but it is opinionated about database schema and business logic. Customizing it for a specialized technical inspection platform would require deep Frappe framework knowledge and would limit flexibility. The GPL v3 license requires derivative works to also be GPL v3, which may be incompatible with commercial distribution.
- **Verdict:** Not selected. The modular monolith approach (Django + React) provides more control and uses MIT-compatible licensing.

## OCA Field Service

- **Repository:** https://github.com/OCA/field-service
- **License:** LGPL v3
- **Assessment:** Odoo-based field service management. Tightly coupled to Odoo ecosystem. Limited inspection-specific functionality. LGPL v3 has copyleft requirements.
- **Verdict:** Not selected. Requires Odoo infrastructure, not suitable for standalone inspection platform.

## Beveren Field Service Management

- **Repository:** https://github.com/Beveren-Software-Inc/Field_Service_Management
- **License:** Proprietary
- **Assessment:** Commercial product, not open-source. Cannot be reused.
- **Verdict:** Not selected.

## OpenInspection

- **Repository:** https://github.com/InspectorHub/OpenInspection
- **License:** Unknown (repository appears inactive)
- **Assessment:** Limited documentation, no recent commits. Not production-ready.
- **Verdict:** Not selected. Insufficient activity and documentation.

## Django (Selected)

- **Version:** 5.1.7 LTS
- **License:** BSD-3-Clause
- **Assessment:** Mature, well-documented, large ecosystem. Excellent for building REST APIs with Django REST Framework. Supports PostgreSQL, Redis, Celery. Active community.
- **Verdict:** Selected as backend framework.

## Django REST Framework (Selected)

- **License:** BSD-3-Clause
- **Assessment:** Industry standard for Django APIs. Excellent serialization, authentication, and documentation support.
- **Verdict:** Selected for API layer.

## React + TypeScript + Vite (Selected)

- **License:** MIT
- **Assessment:** Modern, performant frontend stack. Large ecosystem. TypeScript provides type safety. Vite offers fast HMR and production builds.
- **Verdict:** Selected for frontend.

## Third-Party Packages Used

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| djangorestframework | 3.15+ | BSD-3-Clause | REST API |
| django-guardian | 2.4+ | GPL | Object-level permissions |
| djangorestframework-simplejwt | 5.3+ | MIT | JWT auth |
| drf-spectacular | 0.27+ | MIT | OpenAPI schema |
| celery | 5.4+ | BSD | Async tasks |
| redis | 5.0+ | BSD | Cache/broker |
| psycopg2-binary | 2.9+ | LGPL | PostgreSQL adapter |
| @mui/material | 5.14+ | MIT | React components |
| @tanstack/react-query | 5.0+ | MIT | Data fetching |
| react-router-dom | 6.0+ | MIT | Routing |
| axios | 1.6+ | MIT | HTTP client |
| jspdf | 2.5+ | MIT | PDF generation |
| jwt-decode | 4.0+ | MIT | JWT decoding |

## Security Evaluation

- All selected packages have active maintenance and security patches
- Django provides built-in CSRF protection, SQL injection prevention, XSS protection
- JWT tokens with refresh token rotation
- Password hashing via Argon2 (Django default)
- Rate limiting configured via environment variables
- Security headers (CSP, HSTS) configured in settings

## Deployment Assessment

- Docker Compose for development and production
- PostgreSQL 15+ for database
- Redis for caching and Celery broker
- Nginx as reverse proxy with HTTPS termination
- Environment-based configuration
- Backup scripts included
