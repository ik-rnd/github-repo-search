"""
URL patterns for the search application.

Endpoints:
    POST /api/search/       — search GitHub users or repositories
    POST /api/clear-cache/  — flush all cached search results from Redis
"""
from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.SearchView.as_view(), name="search"),
    path("clear-cache/", views.ClearCacheView.as_view(), name="clear-cache"),
]
