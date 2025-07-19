from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path(
        "instagram/login/", views.InstagramLoginView.as_view(), name="instagram_login"
    ),
    path(
        "instagram/callback/",
        views.InstagramCallbackView.as_view(),
        name="instagram_callback",
    ),
    path("me/quit/", views.quit, name="quit"),
]
