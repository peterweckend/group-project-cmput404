"""project404_t8 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf.urls import url, include
from .router import router
from rest_framework.authtoken import views
from django.conf.urls.static import static
from django.conf import settings
from API.viewsets import *
from API import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')), 
    path('', homeListView, name='home'),
    url(r'^', include(router.urls)),
    url(r'^',include('API.urls')), 
    url(r'^',include('users.urls')),
    url(r'^deletePost/(?P<pk>\d+)/$', PostDelete.as_view(), name="delete_post"),
    url(r'^deleteFriend/(?P<pk>\d+)/$', FriendDelete.as_view(), name="delete_friend")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
