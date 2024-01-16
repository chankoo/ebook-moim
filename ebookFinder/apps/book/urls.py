from django.urls import path
from ebookFinder.apps.book import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('list/', views.BookListView.as_view(), name='list'),
    path('<isbn_slug>/', views.BookDetailView.as_view(), name='detail'),
]
