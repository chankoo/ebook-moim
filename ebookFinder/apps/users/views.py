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


@login_required
def quit(request):
    """
    사용자 데이터 삭제 안내 및 실제 삭제 처리
    """
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "계정이 완전히 삭제되었습니다.")
        return redirect("book:index")  # 메인 페이지 등으로 리다이렉트
    return render(request, "quit.html")
