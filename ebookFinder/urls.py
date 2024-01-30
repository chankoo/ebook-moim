from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from ebookFinder.apps.book.views import IndexView
from .apis import api

urlpatterns = [
    path('', IndexView.as_view()),
    path('admin/', admin.site.urls),
    path('book/', include('ebookFinder.apps.book.urls')),
    path('api/', api.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

