from django.shortcuts import redirect
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
