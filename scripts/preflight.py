#!/usr/bin/env python3
"""Offline project preflight checks; no services or third-party packages required."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
checks = [
    (ROOT / "backend/config/settings_production.py", "production Django settings"),
    (ROOT / "frontend/nginx.conf", "frontend nginx config (required by Dockerfile)"),
    (ROOT / "docker-compose.yml", "development Compose file"),
    (ROOT / "docker-compose.production.yml", "production Compose file"),
    (ROOT / "backend/requirements/base.txt", "backend requirements"),
    (ROOT / "frontend/package-lock.json", "frontend lockfile"),
]
for path, label in checks:
    if path.exists():
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label}: missing {path.relative_to(ROOT)}")
        errors.append(label)

try:
    package = json.loads((ROOT / "frontend/package.json").read_text())
    lock = json.loads((ROOT / "frontend/package-lock.json").read_text())
    root_lock = lock.get("packages", {}).get("", {})
    for group in ("dependencies", "devDependencies"):
        if package.get(group, {}) != root_lock.get(group, {}):
            errors.append(f"frontend package-lock mismatch in {group}")
            print(f"FAIL  package.json and lockfile {group} do not match")
        else:
            print(f"PASS  package.json and lockfile {group} match")
except Exception as exc:
    errors.append("frontend package metadata")
    print(f"FAIL  frontend package metadata: {exc}")

apps = ["accounts", "clients", "projects", "inspections", "notifications", "reports", "mts", "documents", "audit"]
missing = []
for app in apps:
    folder = ROOT / "backend/apps" / app / "migrations"
    if not folder.exists() or not any(p.name.endswith(".py") and p.name != "__init__.py" for p in folder.iterdir()):
        missing.append(app)
if missing:
    print("BLOCK  Versioned initial migrations are missing for: " + ", ".join(missing))
    print("       Run scripts/generate_migrations.sh in an environment with backend requirements installed, review and commit the generated files.")
    errors.append("versioned initial migrations")
else:
    print("PASS  Versioned application migrations exist")

if errors:
    print("\nPreflight failed: " + "; ".join(errors))
    sys.exit(1)
print("\nPreflight checks completed. This is a static check, not a substitute for integration/security tests.")
