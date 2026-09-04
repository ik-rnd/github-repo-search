import pytest
import jwt
import datetime
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def valid_token():
    payload = {
        "provider": "github",
        "access_token": "dummy_access_token",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

@pytest.mark.django_db
@patch("search.action_views.requests.put")
def test_star_repo_success(mock_put, api_client, valid_token):
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_put.return_value = mock_response

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_token}')
    response = api_client.post(
        "/api/repos/star/",
        data={"repo_full_name": "facebook/react"},
        format="json"
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": True}
    mock_put.assert_called_once()

@pytest.mark.django_db
def test_star_repo_unauthenticated(api_client):
    response = api_client.post(
        "/api/repos/star/",
        data={"repo_full_name": "facebook/react"},
        format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
@patch("search.action_views.requests.post")
def test_fork_repo_success(mock_post, api_client, valid_token):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_token}')
    response = api_client.post(
        "/api/repos/fork/",
        data={"repo_full_name": "facebook/react"},
        format="json"
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": True}
    mock_post.assert_called_once()
