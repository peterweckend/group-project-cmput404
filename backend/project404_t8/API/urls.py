from django.urls import path
from .views import ListPostsView


urlpatterns = [
    path('posts/', ListPostsView.as_view(), name="posts-all")
]
