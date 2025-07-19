import pytest
import requests
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.contrib.auth import get_user_model
from .. import services

User = get_user_model()


@pytest.fixture(autouse=True)
def override_insta_settings(settings):
    """
    Fixture to override Instagram settings for all tests in this module.
    """
    settings.INSTAGRAM_CLIENT_ID = "test_client_id"
    settings.INSTAGRAM_CLIENT_SECRET = "test_client_secret"
    settings.INSTAGRAM_REDIRECT_URI = "https://test.com/callback"


def test_get_instagram_auth_url():
    """
    Test that the Instagram auth URL is generated correctly.
    """
    url = services.get_instagram_auth_url()
    assert "https://api.instagram.com/oauth/authorize" in url
    assert f"client_id={settings.INSTAGRAM_CLIENT_ID}" in url
    assert f"redirect_uri={settings.INSTAGRAM_REDIRECT_URI}" in url
    assert "scope=user_profile,user_media" in url
    assert "response_type=code" in url


@patch("apps.users.services.requests.post")
def test_exchange_code_for_token_success(mock_post):
    """
    Test successfully exchanging an authorization code for an access token.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token", "user_id": "123"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    token_data = services.exchange_code_for_token("test_code")

    assert token_data == {"access_token": "test_token", "user_id": "123"}
    mock_post.assert_called_once()


@patch("apps.users.services.requests.post")
def test_exchange_code_for_token_failure(mock_post):
    """
    Test failure case for exchanging code for token.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        services.exchange_code_for_token("test_code")


@patch("apps.users.services.requests.get")
def test_get_instagram_user_profile_success(mock_get):
    """
    Test successfully fetching the user profile from Instagram.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "test_ig_id", "username": "testuser"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    profile_data = services.get_instagram_user_profile("test_access_token")

    assert profile_data == {"id": "test_ig_id", "username": "testuser"}
    mock_get.assert_called_once_with("https://graph.instagram.com/me?fields=id,username&access_token=test_access_token")


@pytest.mark.django_db
def test_get_or_create_user_creates_new_user():
    """
    Test that a new user is created if they don't exist.
    """
    assert User.objects.count() == 0
    user_data = {"id": "new_ig_id", "username": "newuser"}
    user = services.get_or_create_user(user_data)

    assert User.objects.count() == 1
    assert user.instagram_id == "new_ig_id"
    assert user.username == "newuser"


@pytest.mark.django_db
def test_get_or_create_user_gets_existing_user():
    """
    Test that an existing user is retrieved.
    """
    existing_user = User.objects.create_user(instagram_id="existing_ig_id", username="existinguser")
    assert User.objects.count() == 1

    user_data = {"id": "existing_ig_id", "username": "existinguser"}
    user = services.get_or_create_user(user_data)

    assert User.objects.count() == 1
    assert user == existing_user


@pytest.mark.django_db
def test_get_jwt_for_user():
    """
    Test that JWT tokens are generated for a user.
    """
    user = User.objects.create_user(instagram_id="test_ig_id", username="testuser")
    tokens = services.get_jwt_for_user(user)

    assert "refresh" in tokens
    assert "access" in tokens
    assert isinstance(tokens["refresh"], str)
    assert isinstance(tokens["access"], str)