from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path(
        "<str:provider>/login/",
        views.OAuthLoginRedirectView.as_view(),
        name="oauth_login",
    ),
    path(
        "<str:provider>/callback/",
        views.OAuthCallbackView.as_view(),
        name="oauth_callback",
    ),
    path("me/quit/", views.quit, name="quit"),
]
