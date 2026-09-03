"""
Git providers API client for the search application.

Wraps the Search API endpoints for GitHub, GitLab, and Bitbucket.
"""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime, timezone

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class GitAPIError(Exception):
    """Raised when the API returns an unexpected response."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def _build_github_headers() -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = getattr(settings, "GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def search_github(entity_type: str, query: str) -> dict[str, Any]:
    endpoints = {
        "users": "/search/users",
        "repositories": "/search/repositories",
    }
    endpoint = f"{settings.GITHUB_API_BASE_URL}{endpoints[entity_type]}"
    params = {"q": query, "per_page": settings.GITHUB_SEARCH_PER_PAGE}

    try:
        response = requests.get(
            endpoint, headers=_build_github_headers(), params=params, timeout=30
        )
    except requests.exceptions.Timeout as exc:
        logger.error("GitHub API timeout: %s", exc)
        raise GitAPIError("GitHub API request timed out.", status_code=504) from exc
    except requests.exceptions.RequestException as exc:
        raise GitAPIError(f"Failed to reach GitHub API: {exc}", status_code=502) from exc

    if response.status_code == 403:
        raise GitAPIError("GitHub API rate limit exceeded.", status_code=429)
    if response.status_code == 422:
        raise GitAPIError("Invalid search query.", status_code=400)
    if not response.ok:
        raise GitAPIError(f"GitHub API error: {response.status_code}", status_code=502)

    data = response.json()
    data["entity_type"] = entity_type
    return data


def search_gitlab(entity_type: str, query: str) -> dict[str, Any]:
    # GitLab API v4
    base_url = "https://gitlab.com/api/v4"
    per_page = getattr(settings, "GITHUB_SEARCH_PER_PAGE", 30)
    
    if entity_type == "users":
        url = f"{base_url}/users"
        params = {"search": query, "per_page": per_page}
    else:
        url = f"{base_url}/projects"
        params = {"search": query, "per_page": per_page}
        
    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise GitAPIError(f"Failed to reach GitLab API: {exc}", status_code=502) from exc

    if response.status_code == 429:
        raise GitAPIError("GitLab API rate limit exceeded.", status_code=429)
    if not response.ok:
        raise GitAPIError(f"GitLab API error: {response.status_code}", status_code=502)

    items = response.json()
    total_count = int(response.headers.get("x-total", len(items)))
    
    # Map to GitHub shape
    mapped_items = []
    for item in items:
        if entity_type == "users":
            mapped_items.append({
                "id": item.get("id"),
                "login": item.get("username"),
                "avatar_url": item.get("avatar_url"),
                "html_url": item.get("web_url"),
                "type": "User",
                "score": 1.0,
            })
        else:
            mapped_items.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "full_name": item.get("path_with_namespace"),
                "description": item.get("description"),
                "html_url": item.get("web_url"),
                "stargazers_count": item.get("star_count", 0),
                "forks_count": item.get("forks_count", 0),
                "open_issues_count": item.get("open_issues_count", 0),
                "language": None,
                "owner": {
                    "login": item.get("namespace", {}).get("path", ""),
                    "avatar_url": item.get("namespace", {}).get("avatar_url", ""),
                    "html_url": item.get("namespace", {}).get("web_url", ""),
                },
                "updated_at": item.get("last_activity_at", datetime.now(timezone.utc).isoformat()),
                "watchers_count": 0,
                "topics": item.get("topics", []),
            })
            
    return {
        "total_count": total_count,
        "items": mapped_items,
        "entity_type": entity_type
    }


def search_codeberg(entity_type: str, query: str) -> dict[str, Any]:
    # Codeberg API v1 (Gitea compatible)
    base_url = "https://codeberg.org/api/v1"
    per_page = getattr(settings, "GITHUB_SEARCH_PER_PAGE", 30)
    
    if entity_type == "users":
        url = f"{base_url}/users/search"
        params = {"q": query, "limit": per_page}
    else:
        url = f"{base_url}/repos/search"
        params = {"q": query, "limit": per_page}
        
    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise GitAPIError(f"Failed to reach Codeberg API: {exc}", status_code=502) from exc

    if response.status_code == 429:
        raise GitAPIError("Codeberg API rate limit exceeded.", status_code=429)
    if not response.ok:
        raise GitAPIError(f"Codeberg API error: {response.status_code}", status_code=502)

    data = response.json()
    items = data.get("data", [])
    total_count = len(items)  # Codeberg doesn't always return total count in search responses
    
    mapped_items = []
    for item in items:
        if entity_type == "users":
            mapped_items.append({
                "id": item.get("id", str(hash(item.get("username")))),
                "login": item.get("username", item.get("login")),
                "avatar_url": item.get("avatar_url", ""),
                "html_url": item.get("html_url", f"https://codeberg.org/{item.get('username')}"),
                "type": "User",
                "score": 1.0,
            })
        else:
            mapped_items.append({
                "id": item.get("id", str(hash(item.get("full_name")))), 
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "description": item.get("description"),
                "html_url": item.get("html_url", ""),
                "stargazers_count": item.get("stars_count", 0), 
                "forks_count": item.get("forks_count", 0),
                "open_issues_count": item.get("open_issues_count", 0),
                "language": item.get("language"),
                "owner": {
                    "login": item.get("owner", {}).get("login", ""),
                    "avatar_url": item.get("owner", {}).get("avatar_url", ""),
                    "html_url": item.get("owner", {}).get("html_url", ""),
                },
                "updated_at": item.get("updated_at", datetime.now(timezone.utc).isoformat()),
                "watchers_count": item.get("watchers_count", 0),
                "topics": [],
            })
            
    # Fix IDs to be integers since serializers require int
    for mapped in mapped_items:
        if isinstance(mapped["id"], str):
            mapped["id"] = abs(hash(mapped["id"])) % (10 ** 8)
            
    return {
        "total_count": total_count,
        "items": mapped_items,
        "entity_type": entity_type
    }


def search_provider(provider: str, entity_type: str, query: str) -> dict[str, Any]:
    """
    Search a given git provider.
    """
    if entity_type not in ["users", "repositories"]:
        raise ValueError(f"Unsupported entity_type '{entity_type}'.")
        
    if provider == "github":
        return search_github(entity_type, query)
    elif provider == "gitlab":
        return search_gitlab(entity_type, query)
    elif provider == "codeberg":
        return search_codeberg(entity_type, query)
    else:
        raise ValueError(f"Unsupported provider '{provider}'.")
