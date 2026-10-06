#!/usr/bin/env python3
"""Create the role groups expected by config.access_control; does not assign users."""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.contrib.auth.models import Group
from apps.accounts.roles import ROLE_CHOICES

for key, _label in ROLE_CHOICES:
    group, created = Group.objects.get_or_create(name=key)
    print(("CREATED " if created else "EXISTS  ") + group.name)
print("Assign users to groups only after reviewing least-privilege role requirements.")
