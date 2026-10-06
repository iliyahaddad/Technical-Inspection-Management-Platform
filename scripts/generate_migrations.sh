#!/usr/bin/env sh
# Generates the initial migrations ONCE. Run from the repository root:
#   sh scripts/generate_migrations.sh
# Uses the development image, so nothing needs to be installed on the host. Review, then commit backend/apps/*/migrations.
set -eu
cd "$(dirname "$0")/.."
docker compose run --rm --no-deps -e DJANGO_SETTINGS_MODULE=config.settings_test backend \
  sh -c "python manage.py makemigrations accounts clients projects inspections notifications reports mts documents audit && python manage.py makemigrations --check --dry-run && python manage.py showmigrations"
echo "Now review the new files under backend/apps/*/migrations/ and commit them."
