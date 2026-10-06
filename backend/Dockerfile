FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# fonts-dejavu-core: Unicode/Arabic-script glyphs for PDF generation (drop Vazirmatn into static/fonts for a nicer look)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    fonts-dejavu-core \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt
COPY --chown=app:app . .
RUN mkdir -p /app/media /app/staticfiles && chown -R app:app /app/media /app/staticfiles
EXPOSE 8000

FROM base AS development
RUN pip install -r requirements/development.txt
USER app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS production
# Test/lint-only dependencies are intentionally excluded; runs as an unprivileged user.
USER app
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
