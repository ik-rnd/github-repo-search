import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
@pytest.mark.parametrize("provider,expected_domain", [
    ("github", "github.com/login/oauth/authorize"),
    ("gitlab", "gitlab.com/oauth/authorize"),
    ("codeberg", "codeberg.org/login/oauth/authorize"),
])
def test_login_returns_url(api_client, provider, expected_domain):
    response = api_client.get(f"/api/auth/{provider}/login/")
    assert response.status_code == status.HTTP_200_OK
    assert "url" in response.json()
    assert expected_domain in response.json()["url"]

@pytest.mark.django_db
def test_login_invalid_provider(api_client):
    response = api_client.get("/api/auth/unknown/login/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
@pytest.mark.parametrize("provider", ["github", "gitlab", "codeberg"])
@patch("search.auth_views.requests.post")
def test_callback_successful(mock_post, api_client, provider):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": f"{provider}_dummy_token"}
    mock_post.return_value = mock_response

    response = api_client.post(
        f"/api/auth/{provider}/callback/",
        data={"code": "12345"},
        format="json"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert data["provider"] == provider

@pytest.mark.django_db
@pytest.mark.parametrize("provider", ["github", "gitlab", "codeberg"])
@patch("search.auth_views.requests.post")
def test_callback_missing_code(mock_post, api_client, provider):
    response = api_client.post(f"/api/auth/{provider}/callback/", data={}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
