"""
URL patterns for the search application.

Endpoints:
    POST /api/search/       — search Git users or repositories
    POST /api/clear-cache/  — flush all cached search results from Redis
"""
from django.urls import path

from . import views
from . import auth_views
from . import action_views

urlpatterns = [
    path("search/", views.SearchView.as_view(), name="search"),
    path("clear-cache/", views.ClearCacheView.as_view(), name="clear-cache"),
    path("auth/<str:provider>/login/", auth_views.OAuthLoginView.as_view(), name="auth-login"),
    path("auth/<str:provider>/callback/", auth_views.OAuthCallbackView.as_view(), name="auth-callback"),
    path("repos/star/", action_views.StarRepoView.as_view(), name="repo-star"),
    path("repos/fork/", action_views.ForkRepoView.as_view(), name="repo-fork"),
    path("ping/", views.PingView.as_view(), name="ping"),
]
