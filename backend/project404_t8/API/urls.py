from django.urls import path,include
# from .views import ListPostsView
from . import viewsets
from django.contrib import admin

from django.views.generic import TemplateView
from django.conf.urls import url

urlpatterns = [
    path('/',viewsets.names),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('posts/', ListPostsView.as_view(), name="posts-all")
]
