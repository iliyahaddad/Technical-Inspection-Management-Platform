import pytest
from django.contrib.auth.models import Group


def grant(user, *roles):
    """Attach role groups (the source of truth for permissions, see config.access_control)."""
    for role in roles:
        user.groups.add(Group.objects.get_or_create(name=role)[0])
    return user


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
