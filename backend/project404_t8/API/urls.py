from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

# from . import views
from .viewsets import PostViewSet, uploadView, postView ,IndexView, profileView, friendRequestView

urlpatterns =[
    # path('',uploadView, name="post_list"),
    path("upload/", uploadView, name="Upload"),
    path("post/<int:id>", postView, name="Post"),
    # path("profile/", profileView, name="profile"),
    url(r'profile/(?P<username>[a-zA-Z0-9]+)$', profileView, name='profile'),
    path("friendrequest/", friendRequestView, name="Friend Request")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
