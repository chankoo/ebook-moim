import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient

# Import the view module to patch the services object within it
from ebookFinder.apps.users import views
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_instagram_login_view(api_client, settings):
    """
    Test that the Instagram login view redirects correctly.
    """
    settings.INSTAGRAM_CLIENT_ID = "test_client_id"
    settings.INSTAGRAM_REDIRECT_URI = "https://test.com/callback"
    url = reverse("users:instagram_login")
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


def add_session_to_client(client):
    """
    테스트 클라이언트에 세션 미들웨어를 적용하는 헬퍼 함수
    """
    middleware = SessionMiddleware(lambda req: None)
    for request in [client.request()]:
        middleware.process_request(request)
        request.session.save()


@pytest.mark.django_db
def test_google_login_redirect(client):
    """
    /users/google/login/으로 GET 요청 시 Google 인증 페이지로 리디렉션되는지 테스트
    """
    response = client.get(reverse("users:google_login"))
    assert response.status_code == 302
    assert response.url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    assert "oauth_state" in client.session


import pytest
from unittest.mock import patch


@pytest.fixture
def google_callback_url():
    return reverse("users:google_callback")


@pytest.fixture
def set_session_state(client):
    session = client.session
    session["oauth_state"] = "test_state"
    session.save()
    return client


@pytest.mark.django_db
@patch("requests.post")
@patch("requests.get")
def test_callback_success_new_user(
    mock_get, mock_post, set_session_state, google_callback_url
):
    """
    Google 콜백 성공 및 신규 사용자 생성 테스트
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    client = set_session_state
    mock_post.return_value.json.return_value = {"access_token": "test_token"}
    mock_get.return_value.json.return_value = {
        "email": "newuser@test.com",
        "given_name": "New",
        "family_name": "User",
    }
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"
    assert User.objects.filter(email="newuser@test.com").exists()
    user = User.objects.get(email="newuser@test.com")
    assert str(client.session["_auth_user_id"]) == str(user.id)


@pytest.mark.django_db
@patch("requests.post")
@patch("requests.get")
def test_callback_success_existing_user(
    mock_get, mock_post, set_session_state, google_callback_url
):
    """
    Google 콜백 성공 및 기존 사용자 로그인 테스트
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    client = set_session_state
    existing_user = User.objects.create_user(
        username="existinguser", email="existing@test.com"
    )
    mock_post.return_value.json.return_value = {"access_token": "test_token"}
    mock_get.return_value.json.return_value = {"email": "existing@test.com"}
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"
    assert int(client.session["_auth_user_id"]) == existing_user.id
    assert User.objects.count() == 1  # 새로운 유저가 생성되지 않았는지 확인


@pytest.mark.django_db
@patch("requests.post")
@patch("requests.get")
def test_callback_fail_state_mismatch(mock_get, mock_post, client, google_callback_url):
    """
    CSRF 방어: state 값이 일치하지 않을 때 실패하는지 테스트
    """
    session = client.session
    session["oauth_state"] = "test_state"
    session.save()
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "wrong_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"
    assert "_auth_user_id" not in client.session  # 로그인되지 않았는지 확인


@pytest.mark.django_db
@patch("requests.post")
@patch("requests.get")
def test_callback_fail_no_access_token(
    mock_get, mock_post, set_session_state, google_callback_url
):
    """
    Access Token 발급에 실패했을 때 로그인 실패하는지 테스트
    """
    client = set_session_state
    mock_post.return_value.json.return_value = {"error": "invalid_grant"}
    response = client.get(
        google_callback_url, {"code": "test_code", "state": "test_state"}
    )
    assert response.status_code == 302
    assert response.url == "/"
    assert "_auth_user_id" not in client.session
