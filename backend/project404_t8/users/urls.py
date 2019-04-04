from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.urls import path
from . import views
from API.viewsets import postView
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    # url(r'^/(?P<id>[a-zA-Z0-9-_]+)$', postView, name = 'Post'),
    path("profile/post/<id>", postView, name="Post"),
]