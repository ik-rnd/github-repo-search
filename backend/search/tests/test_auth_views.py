import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_login_returns_url(api_client):
    response = api_client.get("/api/auth/github/login/")
    assert response.status_code == status.HTTP_200_OK
    assert "url" in response.json()
    assert "github.com/login/oauth/authorize" in response.json()["url"]

@pytest.mark.django_db
def test_login_invalid_provider(api_client):
    response = api_client.get("/api/auth/unknown/login/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
@patch("search.auth_views.requests.post")
def test_callback_successful(mock_post, api_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "dummy_token"}
    mock_post.return_value = mock_response

    response = api_client.post(
        "/api/auth/github/callback/",
        data={"code": "12345"},
        format="json"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert data["provider"] == "github"

@pytest.mark.django_db
@patch("search.auth_views.requests.post")
def test_callback_missing_code(mock_post, api_client):
    response = api_client.post("/api/auth/github/callback/", data={}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
