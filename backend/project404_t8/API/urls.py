from django.urls import path
from django.conf.urls import  url 

# from . import views
from .viewsets import uploadView,PostViewSet
urlpatterns =[
    # path('',uploadView, name="post_list"),
    path("upload/", uploadView, name="upload"),
]