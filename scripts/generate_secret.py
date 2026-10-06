#!/usr/bin/env python3
"""Print a cryptographically strong Django SECRET_KEY candidate."""
import secrets

print(secrets.token_urlsafe(64))
