import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from abc import ABC, abstractmethod

User = get_user_model()


def get_instagram_auth_url():
    """
    인스타그램 OAuth2 인가 엔드포인트 URL을 생성합니다.
    """
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={settings.INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={settings.INSTAGRAM_REDIRECT_URI}"
        f"&scope=user_profile,user_media"
        f"&response_type=code"
    )
    return auth_url


def exchange_code_for_token(code: str) -> dict:
    """
    인가 코드를 사용하여 액세스 토큰을 요청합니다.
    """
    token_url = "https://api.instagram.com/oauth/access_token"
    data = {
        "client_id": settings.INSTAGRAM_CLIENT_ID,
        "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "code": code,
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()


def get_instagram_user_profile(access_token: str) -> dict:
    """
    액세스 토큰을 사용하여 인스타그램 사용자 프로필 정보를 가져옵니다.
    """
    user_profile_url = (
        f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
    )
    response = requests.get(user_profile_url)
    response.raise_for_status()
    return response.json()


def get_or_create_user(user_data: dict):
    """
    인스타그램 사용자 정보를 바탕으로 유저를 생성하거나 가져옵니다.
    """
    instagram_id = user_data["id"]
    username = user_data["username"]

    user, created = User.objects.get_or_create(
        instagram_id=instagram_id,
        defaults={"username": username},
    )
    return user


def get_jwt_for_user(user):
    """
    사용자 객체에 대한 JWT 토큰을 생성합니다.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_google_auth_url(state):
    """
    구글 OAuth2 인증 엔드포인트 URL을 생성합니다.
    """
    from django.conf import settings

    GOOGLE_OAUTH_AUTHORIZE_URI = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
        "state": state,
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{GOOGLE_OAUTH_AUTHORIZE_URI}?{query_string}"


def exchange_google_code_for_token(code: str) -> dict:
    """
    구글 인가 코드를 사용하여 액세스 토큰을 요청합니다.
    """
    from django.conf import settings

    token_uri = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }
    response = requests.post(token_uri, data=data)
    response.raise_for_status()
    return response.json()


def get_google_user_profile(access_token: str) -> dict:
    """
    구글 액세스 토큰을 사용하여 사용자 프로필 정보를 가져옵니다.
    """
    user_info_uri = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_uri, headers=headers)
    response.raise_for_status()
    return response.json()


def get_or_create_google_user(user_data: dict):
    """
    구글 사용자 정보를 바탕으로 유저를 생성하거나 가져옵니다.
    """
    email = user_data["email"]
    username = email.split("@")[0]
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": username},
    )
    return user


class OAuthProviderBase(ABC):
    @abstractmethod
    def get_auth_url(self, state): ...
    @abstractmethod
    def exchange_code_for_token(self, code): ...
    @abstractmethod
    def get_user_profile(self, access_token): ...
    @abstractmethod
    def get_or_create_user(self, user_data): ...
    @abstractmethod
    def login_response(self, request, user): ...


class GoogleOAuthProvider(OAuthProviderBase):
    def get_auth_url(self, state):
        return get_google_auth_url(state)

    def exchange_code_for_token(self, code):
        return exchange_google_code_for_token(code)

    def get_user_profile(self, access_token):
        return get_google_user_profile(access_token)

    def get_or_create_user(self, user_data):
        return get_or_create_google_user(user_data)

    def login_response(self, request, user):
        from django.contrib.auth import login

        login(request, user)
        from django.shortcuts import redirect

        return redirect("/")


class InstagramOAuthProvider(OAuthProviderBase):
    def get_auth_url(self, state=None):
        return get_instagram_auth_url()

    def exchange_code_for_token(self, code):
        return exchange_code_for_token(code)

    def get_user_profile(self, access_token):
        return get_instagram_user_profile(access_token)

    def get_or_create_user(self, user_data):
        return get_or_create_user(user_data)

    def login_response(self, request, user):
        # JWT 발급 후 JSON 반환
        from django.http import JsonResponse

        if user is None:
            return JsonResponse({"error": "User not found"}, status=400)
        token = get_jwt_for_user(user)
        return JsonResponse(token)
