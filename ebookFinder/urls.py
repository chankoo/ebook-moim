# -*- coding:utf-8 -*-

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('book/', include('ebookFinder.apps.book.urls')),
]
