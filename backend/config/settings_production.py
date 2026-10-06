"""Hardened production settings. All secrets and deployment-specific values are required."""
import os
from urllib.parse import unquote, urlparse
from django.core.exceptions import ImproperlyConfigured
from .settings import *  # noqa: F403,F401

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith(("change-me", "REPLACE", "dev-")):
    raise ImproperlyConfigured("Set SECRET_KEY to a randomly generated value of at least 50 characters.")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set ALLOWED_HOSTS to the public hostnames for this deployment.")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is required in production.")
parsed = urlparse(DATABASE_URL)
if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname or not parsed.path.strip("/"):
    raise ImproperlyConfigured("DATABASE_URL must be a valid PostgreSQL URL.")
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": unquote(parsed.path.lstrip("/")),
    "USER": unquote(parsed.username or ""),
    "PASSWORD": unquote(parsed.password or ""),
    "HOST": parsed.hostname,
    "PORT": parsed.port or 5432,
    "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
    "CONN_HEALTH_CHECKS": True,
    "OPTIONS": {"connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10"))},
}}
if os.environ.get("DB_SSL_REQUIRE", "false").lower() == "true":
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000" if SECURE_SSL_REDIRECT else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": [  # noqa: F405
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
], "DEFAULT_THROTTLE_RATES": {"anon": os.environ.get("API_ANON_RATE", "60/min"), "user": os.environ.get("API_USER_RATE", "600/min")}}

# Production logging goes to stdout/stderr for Docker log collection.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}

# Trusted proxy hops (nginx + TLS terminator by default) for audit-log IPs and throttling.
NUM_PROXIES = int(os.environ.get("NUM_PROXIES", "2"))
USE_X_ACCEL_REDIRECT = os.environ.get("USE_X_ACCEL_REDIRECT", "true").lower() == "true"
