from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ebookFinder.apps.users import services
from .services import GoogleOAuthProvider, InstagramOAuthProvider

OAUTH_PROVIDERS = {
    "google": GoogleOAuthProvider(),
    "instagram": InstagramOAuthProvider(),
}


def get_oauth_provider(provider_name):
    return OAUTH_PROVIDERS[provider_name]


from django.views import View
from django.views.generic import RedirectView
from django.shortcuts import redirect
import uuid


class OAuthLoginRedirectView(RedirectView):
    def get(self, request, *args, **kwargs):
        provider_name = kwargs["provider"]
        provider = get_oauth_provider(provider_name)
        state = str(uuid.uuid4()) if provider_name == "google" else None
        if state:
            request.session["oauth_state"] = state
        return redirect(provider.get_auth_url(state))


class OAuthCallbackView(View):
    def get(self, request, *args, **kwargs):
        provider_name = kwargs["provider"]
        provider = get_oauth_provider(provider_name)
        # state 검증 (구글만)
        if provider_name == "google":
            if request.GET.get("state") != request.session.get("oauth_state"):
                return redirect("/")
        code = request.GET.get("code")
        if not code:
            return (
                redirect("/")
                if provider_name == "google"
                else provider.login_response(request, None)
            )
        try:
            token_data = provider.exchange_code_for_token(code)
            access_token = token_data.get("access_token")
            if not access_token:
                return (
                    redirect("/")
                    if provider_name == "google"
                    else provider.login_response(request, None)
                )
            user_data = provider.get_user_profile(access_token)
            user = provider.get_or_create_user(user_data)
            if user is None:
                if provider_name == "instagram":
                    from django.http import JsonResponse

                    return JsonResponse({"error": "User not found"}, status=400)
                return redirect("/")
            return provider.login_response(request, user)
        except Exception:
            if provider_name == "instagram":
                from django.http import JsonResponse

                return JsonResponse({"error": "Exception occurred"}, status=400)
            return redirect("/")


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
