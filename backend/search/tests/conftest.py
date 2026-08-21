"""
conftest.py — pytest-django fixtures shared across the search test suite.
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def use_locmem_cache(settings):
    """
    Override the cache backend to use Django's in-memory cache for all tests.
    Using the pytest-django ``settings`` fixture ensures Django sees the change
    before any module-level cache proxy is evaluated.
    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    # Clear any left-overs from previous tests
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
