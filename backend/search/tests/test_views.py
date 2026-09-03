"""
Unit tests for the GitHub search API views and the GitHub client.

All GitHub API calls are patched with unittest.mock so tests run
without network or Redis. Cache is overridden to LocMemCache via the
autouse ``use_locmem_cache`` fixture in conftest.py.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status

from search.git_client import GitAPIError

# ---------------------------------------------------------------------------
# Shared fixtures / constants
# ---------------------------------------------------------------------------

SEARCH_URL = "/api/search/"
CLEAR_CACHE_URL = "/api/clear-cache/"

MOCK_REPO_RESPONSE: dict[str, Any] = {
    "total_count": 1,
    "entity_type": "repositories",
    "items": [
        {
            "id": 1296269,
            "name": "Hello-World",
            "full_name": "octocat/Hello-World",
            "description": "My first repository on GitHub!",
            "html_url": "https://github.com/octocat/Hello-World",
            "stargazers_count": 2000,
            "forks_count": 800,
            "open_issues_count": 10,
            "watchers_count": 2000,
            "language": "Python",
            "updated_at": "2024-01-01T00:00:00Z",
            "topics": [],
            "owner": {
                "login": "octocat",
                "avatar_url": "https://avatars.githubusercontent.com/u/583231",
                "html_url": "https://github.com/octocat",
            },
        }
    ],
}

MOCK_USER_RESPONSE: dict[str, Any] = {
    "total_count": 1,
    "entity_type": "users",
    "items": [
        {
            "id": 583231,
            "login": "octocat",
            "avatar_url": "https://avatars.githubusercontent.com/u/583231",
            "html_url": "https://github.com/octocat",
            "type": "User",
            "score": 1.0,
        }
    ],
}

# ---------------------------------------------------------------------------
# SearchView — repository happy paths
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_search_repos_returns_200(mock_gh, api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["entity_type"] == "repositories"
    assert body["total_count"] == 1
    assert len(body["items"]) == 1
    assert body["cached"] is False


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_github_called_once_on_cache_miss(mock_gh, api_client):
    api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    mock_gh.assert_called_once_with(entity_type="repositories", query="django")


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_second_request_served_from_cache(mock_gh, api_client):
    """GitHub API must NOT be called on the second identical request."""
    api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["cached"] is True
    mock_gh.assert_called_once()


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_query_cache_is_case_insensitive(mock_gh, api_client):
    """'Django' and 'django' should share the same cache entry."""
    api_client.post(
        SEARCH_URL,
        data={"query": "Django", "entity_type": "repositories"},
        format="json",
    )
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert response.json()["cached"] is True
    mock_gh.assert_called_once()


# ---------------------------------------------------------------------------
# SearchView — user happy paths
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_USER_RESPONSE)
def test_search_users_returns_200(mock_gh, api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "octocat", "entity_type": "users"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["entity_type"] == "users"
    assert body["items"][0]["login"] == "octocat"


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_different_entity_types_have_separate_cache_keys(mock_gh, api_client):
    """Same query + different entity_type → separate cache entries."""
    api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    # Switch entity type — override the mock return for the second call
    mock_gh.return_value = MOCK_USER_RESPONSE
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "users"},
        format="json",
    )
    assert response.json()["cached"] is False
    assert mock_gh.call_count == 2


# ---------------------------------------------------------------------------
# SearchView — validation errors (no mock needed — never reaches GitHub)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_missing_query_returns_400(api_client):
    response = api_client.post(
        SEARCH_URL, data={"entity_type": "repositories"}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "details" in response.json()


@pytest.mark.django_db
def test_short_query_returns_400(api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "ab", "entity_type": "repositories"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_missing_entity_type_returns_400(api_client):
    response = api_client.post(
        SEARCH_URL, data={"query": "django"}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_invalid_entity_type_returns_400(api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "issues"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_empty_body_returns_400(api_client):
    response = api_client.post(SEARCH_URL, data={}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# SearchView — upstream errors
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@patch(
    "search.views.search_provider",
    side_effect=GitAPIError("GitHub API rate limit exceeded.", status_code=429),
)
def test_rate_limit_returns_429(mock_gh, api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert response.status_code == 429
    assert "error" in response.json()


@pytest.mark.django_db
@patch(
    "search.views.search_provider",
    side_effect=GitAPIError("GitHub API error: 502", status_code=502),
)
def test_github_502_returns_502(mock_gh, api_client):
    response = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert response.status_code == 502


# ---------------------------------------------------------------------------
# ClearCacheView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_clear_cache_returns_200(api_client):
    response = api_client.post(CLEAR_CACHE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


@pytest.mark.django_db
@patch("search.views.search_provider", return_value=MOCK_REPO_RESPONSE)
def test_clear_cache_invalidates_cached_results(mock_gh, api_client):
    # Populate cache
    api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    # Confirm cached
    second = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert second.json()["cached"] is True

    # Clear cache
    api_client.post(CLEAR_CACHE_URL)

    # Next request should be a cache miss
    third = api_client.post(
        SEARCH_URL,
        data={"query": "django", "entity_type": "repositories"},
        format="json",
    )
    assert third.json()["cached"] is False
    assert mock_gh.call_count == 2  # first + third


# ---------------------------------------------------------------------------
# GitHubClient unit tests
# ---------------------------------------------------------------------------


@patch("search.git_client.requests.get")
def test_git_client_successful_repo_search(mock_get):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total_count": 1,
        "items": [{"id": 1, "name": "test-repo"}],
    }
    mock_get.return_value = mock_response

    from search.git_client import search_provider

    result = search_provider("repositories", "django")
    assert result["total_count"] == 1
    assert result["entity_type"] == "repositories"
    mock_get.assert_called_once()


@patch("search.git_client.requests.get")
def test_git_client_rate_limit_raises_error(mock_get):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403
    mock_get.return_value = mock_response

    from search.git_client import search_provider

    with pytest.raises(GitAPIError) as exc_info:
        search_provider("repositories", "django")
    assert exc_info.value.status_code == 429


@patch("search.git_client.requests.get")
def test_git_client_timeout_raises_error(mock_get):
    import requests as req

    mock_get.side_effect = req.exceptions.Timeout("timed out")

    from search.git_client import search_provider

    with pytest.raises(GitAPIError) as exc_info:
        search_provider("users", "octocat")
    assert exc_info.value.status_code == 504


def test_git_client_invalid_entity_type():
    from search.git_client import search_provider

    with pytest.raises(ValueError, match="Unsupported entity_type"):
        search_provider("issues", "test")
