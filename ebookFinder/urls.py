from django.contrib import admin
from django.urls import path, include
from ebookFinder.apps.book.views import IndexView

urlpatterns = [
    path('', IndexView.as_view()),
    path('admin/', admin.site.urls),
    path('book/', include('ebookFinder.apps.book.urls')),
]
