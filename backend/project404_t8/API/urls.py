from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

# from . import views

from .viewsets import uploadView, postView, profileView, friendRequestView, editProfile, comment_thread, friendsView

urlpatterns =[
    # path('',uploadView, name="post_list"),
    path("upload/", uploadView, name="Upload"),
    path("post/<id>", postView, name="Post"),
    path("friends/", friendsView, name="Friends"),
    url(r'^profile/(?P<username>[a-zA-Z0-9-_]+)$', profileView, name='profile'),
    url(r'^editprofile/(?P<pk>[0-9A-Fa-f-]+)/$', editProfile.as_view(), name='editprofile'),
    path("addFriend/", friendRequestView, name="Friend Request"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)