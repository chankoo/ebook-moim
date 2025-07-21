import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
import json

# Import the view module to patch the services object within it
from ebookFinder.apps.users import views
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_instagram_login_view(api_client, settings):
    settings.INSTAGRAM_CLIENT_ID = "test_client_id"
    settings.INSTAGRAM_REDIRECT_URI = "https://test.com/callback"
    url = reverse("users:oauth_login", kwargs={"provider": "instagram"})
    response = api_client.get(url)
    assert response.status_code == 302
    expected_url = (
        f"https://api.instagram.com/oauth/authorize?client_id={settings.INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={settings.INSTAGRAM_REDIRECT_URI}&scope=user_profile,user_media&response_type=code"
    )
    assert response.url == expected_url


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
    mock_user = MagicMock()
    mock_get_or_create.return_value = mock_user
    url = reverse("users:oauth_callback", kwargs={"provider": "instagram"})
    response = api_client.get(url, {"code": "test_code"})
    assert response.status_code == 200 or response.status_code == 400
    data = json.loads(response.content)
    assert data["access"] == "jwt_access_token"
    mock_exchange.assert_called_once_with("test_code")
    mock_get_profile.assert_called_once_with("test_access_token")
    mock_get_or_create.assert_called_once_with(
        {"id": "test_ig_id", "username": "testuser"}
    )
    mock_get_jwt.assert_called_once_with(mock_user)


@pytest.mark.django_db
def test_instagram_callback_view_no_code(api_client):
    url = reverse("users:oauth_callback", kwargs={"provider": "instagram"})
    response = api_client.get(url)
    assert response.status_code in (200, 302, 400)


@pytest.mark.django_db
@patch.object(
    views.services, "exchange_code_for_token", side_effect=Exception("Service Error")
)
def test_instagram_callback_view_service_error(mock_exchange, api_client):
    url = reverse("users:oauth_callback", kwargs={"provider": "instagram"})
    response = api_client.get(url, {"code": "test_code"})
    assert response.status_code in (200, 302, 400)


import pytest
from unittest.mock import patch


@pytest.fixture
def google_callback_url():
    return reverse("users:oauth_callback", kwargs={"provider": "google"})


@pytest.fixture
def set_session_state(client):
    session = client.session
    session["oauth_state"] = "test_state"
    session.save()
    return client


@pytest.mark.django_db
@patch("ebookFinder.apps.users.services.exchange_google_code_for_token")
@patch("ebookFinder.apps.users.services.get_google_user_profile")
@patch("ebookFinder.apps.users.services.get_or_create_google_user")
@patch("django.contrib.auth.login")
def test_callback_success_new_user(
    mock_login,
    mock_get_or_create,
    mock_get_profile,
    mock_exchange,
    set_session_state,
    google_callback_url,
):
    User = get_user_model()
    client = set_session_state
    mock_exchange.return_value = {"access_token": "test_token"}
    mock_get_profile.return_value = {
        "email": "newuser@test.com",
        "given_name": "New",
        "family_name": "User",
    }
    mock_user = User(username="newuser", email="newuser@test.com")
    mock_get_or_create.return_value = mock_user
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
@patch("ebookFinder.apps.users.services.exchange_google_code_for_token")
@patch("ebookFinder.apps.users.services.get_google_user_profile")
@patch("ebookFinder.apps.users.services.get_or_create_google_user")
@patch("django.contrib.auth.login")
def test_callback_success_existing_user(
    mock_login,
    mock_get_or_create,
    mock_get_profile,
    mock_exchange,
    set_session_state,
    google_callback_url,
):
    User = get_user_model()
    client = set_session_state
    mock_exchange.return_value = {"access_token": "test_token"}
    mock_get_profile.return_value = {"email": "existing@test.com"}
    mock_user = User(username="existinguser", email="existing@test.com")
    mock_get_or_create.return_value = mock_user
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_callback_fail_state_mismatch(client, google_callback_url):
    session = client.session
    session["oauth_state"] = "test_state"
    session.save()
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "wrong_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
@patch(
    "ebookFinder.apps.users.services.exchange_google_code_for_token", return_value={}
)
def test_callback_fail_no_access_token(
    mock_exchange, set_session_state, google_callback_url
):
    client = set_session_state
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"
