from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ebookFinder.apps.users import services


class InstagramLoginView(View):
    def get(self, request, *args, **kwargs):
        auth_url = services.get_instagram_auth_url()
        return redirect(auth_url)


class InstagramCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code")
        if not code:
            return Response(
                {"error": "Authorization code not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 1. Exchange code for access token
            token_data = services.exchange_code_for_token(code)
            access_token = token_data["access_token"]

            # 2. Get user profile from Instagram
            user_profile = services.get_instagram_user_profile(access_token)

            # 3. Get or create user in local DB
            user = services.get_or_create_user(user_profile)

            # 4. Generate JWT token
            jwt_token = services.get_jwt_for_user(user)

            return Response(jwt_token, status=status.HTTP_200_OK)

        except Exception as e:
            # You might want to log the error here
            return Response(
                {
                    "error": "An error occurred during authentication.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def quit(request):
    """
    사용자 데이터 삭제 안내 및 실제 삭제 처리
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            user = request.user
            user.delete()
            messages.success(request, "계정이 완전히 삭제되었습니다.")
            return redirect("book:index")  # 메인 페이지 등으로 리다이렉트
        return render(request, "quit.html")
    else:
        # 비로그인 사용자는 안내만 보여줌
        return render(request, "quit.html", {"not_authenticated": True})


import uuid
import requests

from django.views.generic import RedirectView
from django.conf import settings
from django.contrib.auth import get_user_model, login

User = get_user_model()


class GoogleLoginRedirectView(RedirectView):
    """
    사용자를 Google OAuth 2.0 인증 페이지로 리디렉션하는 뷰.
    state 값을 생성하여 세션에 저장한 뒤, Google 인증 URL을 생성하여 이동시킵니다.
    """

    def get_redirect_url(self, *args, **kwargs):
        GOOGLE_OAUTH_AUTHORIZE_URI = "https://accounts.google.com/o/oauth2/v2/auth"

        # CSRF 방지를 위한 state 값 생성 및 세션 저장
        state = str(uuid.uuid4())
        self.request.session["oauth_state"] = state

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
            "state": state,
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GOOGLE_OAUTH_AUTHORIZE_URI}?{query_string}"


class GoogleCallbackView(View):
    """
    Google 로그인 후 콜백을 처리하는 뷰.
    - state 값 검증
    - authorization_code를 사용하여 access_token 발급
    - access_token으로 사용자 정보 조회
    - 사용자 정보로 Django User를 생성 또는 조회하여 로그인 처리
    """

    def get(self, request, *args, **kwargs):
        # 1. CSRF 방어: state 값 검증
        if request.GET.get("state") != request.session.get("oauth_state"):
            return redirect("/")  # 또는 에러 페이지

        # 2. Authorization Code로 Access Token 요청
        code = request.GET.get("code")
        access_token = self._get_access_token(code)
        if not access_token:
            return redirect("/")  # 또는 에러 페이지

        # 3. Access Token으로 사용자 정보 요청
        user_data = self._get_user_info(access_token)
        email = user_data.get("email")
        if not email:
            return redirect("/")  # 또는 에러 페이지

        # 4. 사용자 정보로 로그인/회원가입 처리
        user = self._get_or_create_user(email, user_data)
        login(request, user)

        return redirect("/")  # 로그인 성공 후 메인 페이지로 리디렉션

    def _get_access_token(self, code):
        token_uri = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
        response = requests.post(token_uri, data=data)
        return response.json().get("access_token")

    def _get_user_info(self, access_token):
        user_info_uri = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(user_info_uri, headers=headers)
        return response.json()

    def _get_or_create_user(self, email, user_data):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
            },
        )
        return user
