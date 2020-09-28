# -*- coding:utf-8 -*-

from django.urls import path
from ebookFinder.apps.book import views


urlpatterns = [
    path('', views.IndexView.as_view()),
    path('list/', views.BookListView.as_view()),
    path('<isbn_slug>/', views.BookDetailView.as_view()),
]
