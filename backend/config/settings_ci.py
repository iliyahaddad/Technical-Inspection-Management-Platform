"""CI settings: test-safe defaults with PostgreSQL to exercise production migrations."""
import os
from .settings_test import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "inspection_test"),
        "USER": os.environ.get("PGUSER", "inspection"),
        "PASSWORD": os.environ.get("PGPASSWORD", "test-only-password"),
        "HOST": os.environ.get("PGHOST", "127.0.0.1"),
        "PORT": os.environ.get("PGPORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
}
