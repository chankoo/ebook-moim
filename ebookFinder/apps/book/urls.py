# -*- coding:utf-8 -*-

from django.urls import path
from ebookFinder.apps.book import views


urlpatterns = [
    path('search/', views.MainView.as_view()),
    path('<isbn_slug>/', views.BookDetail.as_view()),
]
