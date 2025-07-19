import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

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
    user_profile_url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
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
