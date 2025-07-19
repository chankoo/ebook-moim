import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient

# Import the view module to patch the services object within it
from apps.users import views


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_instagram_login_view(api_client):
    """
    Test that the Instagram login view redirects correctly.
    """
    url = reverse("users:instagram_login")
    response = api_client.get(url)

    assert response.status_code == 302
    assert (
        response.url
        == "https://api.instagram.com/oauth/authorize?client_id=1950225982466334&redirect_uri=YOUR_INSTAGRAM_REDIRECT_URI&scope=user_profile,user_media&response_type=code"
    )


@pytest.mark.django_db
@patch.object(
    views.services,
    "get_jwt_for_user",
    return_value={"access": "jwt_access_token", "refresh": "jwt_refresh_token"},
)
@patch.object(views.services, "get_or_create_user")
@patch.object(
    views.services,
    "get_instagram_user_profile",
    return_value={"id": "test_ig_id", "username": "testuser"},
)
@patch.object(
    views.services,
    "exchange_code_for_token",
    return_value={"access_token": "test_access_token"},
)
def test_instagram_callback_view_success(
    mock_exchange, mock_get_profile, mock_get_or_create, mock_get_jwt, api_client
):
    """
    Test the full success flow of the Instagram callback.
    """
    mock_user = MagicMock()
    mock_get_or_create.return_value = mock_user

    url = reverse("users:instagram_callback")
    response = api_client.get(url, {"code": "test_code"})

    assert response.status_code == 200
    assert response.data["access"] == "jwt_access_token"

    mock_exchange.assert_called_once_with("test_code")
    mock_get_profile.assert_called_once_with("test_access_token")
    mock_get_or_create.assert_called_once_with(
        {"id": "test_ig_id", "username": "testuser"}
    )
    mock_get_jwt.assert_called_once_with(mock_user)


@pytest.mark.django_db
def test_instagram_callback_view_no_code(api_client):
    """
    Test the callback view when no authorization code is provided.
    """
    url = reverse("users:instagram_callback")
    response = api_client.get(url)

    assert response.status_code == 400
    assert response.data["error"] == "Authorization code not provided"


@pytest.mark.django_db
@patch.object(
    views.services, "exchange_code_for_token", side_effect=Exception("Service Error")
)
def test_instagram_callback_view_service_error(mock_exchange, api_client):
    """
    Test the callback view when a service layer function fails.
    """
    url = reverse("users:instagram_callback")
    response = api_client.get(url, {"code": "test_code"})

    assert response.status_code == 500
    assert "An error occurred during authentication." in response.data["error"]
    assert "Service Error" in response.data["details"]
