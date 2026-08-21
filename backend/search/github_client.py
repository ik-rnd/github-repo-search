"""
GitHub API client for the search application.

Wraps the GitHub REST Search API endpoints for users and repositories.
Uses a personal access token (GITHUB_TOKEN) when available to increase
the rate limit from 10 to 30 requests per minute (unauthenticated vs
authenticated).
"""
from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# GitHub Search API paths keyed by entity type
ENTITY_ENDPOINTS: dict[str, str] = {
    "users": "/search/users",
    "repositories": "/search/repositories",
}


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an unexpected response."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def _build_headers() -> dict[str, str]:
    """Return request headers, including auth if a token is configured."""
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = getattr(settings, "GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def search_github(entity_type: str, query: str) -> dict[str, Any]:
    """
    Search GitHub for users or repositories matching *query*.

    Args:
        entity_type: One of ``"users"`` or ``"repositories"``.
        query: The search string entered by the user.

    Returns:
        The JSON payload returned by the GitHub Search API, augmented with
        the ``entity_type`` field for convenience.

    Raises:
        GitHubAPIError: On non-2xx responses or network errors.
        ValueError: If *entity_type* is not supported.
    """
    if entity_type not in ENTITY_ENDPOINTS:
        raise ValueError(
            f"Unsupported entity_type '{entity_type}'. "
            f"Must be one of: {list(ENTITY_ENDPOINTS)}"
        )

    endpoint = f"{settings.GITHUB_API_BASE_URL}{ENTITY_ENDPOINTS[entity_type]}"
    params = {
        "q": query,
        "per_page": settings.GITHUB_SEARCH_PER_PAGE,
    }

    try:
        response = requests.get(
            endpoint,
            headers=_build_headers(),
            params=params,
            timeout=10,
        )
    except requests.exceptions.Timeout as exc:
        logger.error("GitHub API request timed out: %s", exc)
        raise GitHubAPIError("GitHub API request timed out.", status_code=504) from exc
    except requests.exceptions.RequestException as exc:
        logger.error("GitHub API request failed: %s", exc)
        raise GitHubAPIError(
            f"Failed to reach GitHub API: {exc}", status_code=502
        ) from exc

    if response.status_code == 403:
        logger.warning("GitHub API rate limit exceeded.")
        raise GitHubAPIError(
            "GitHub API rate limit exceeded. Please try again later.",
            status_code=429,
        )

    if response.status_code == 422:
        raise GitHubAPIError(
            "Invalid search query sent to GitHub API.",
            status_code=400,
        )

    if not response.ok:
        logger.error(
            "GitHub API returned %s: %s", response.status_code, response.text
        )
        raise GitHubAPIError(
            f"GitHub API error: {response.status_code}",
            status_code=502,
        )

    data: dict[str, Any] = response.json()
    data["entity_type"] = entity_type
    return data
