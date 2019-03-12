from django.urls import path
from django.conf.urls import  url 
from django.conf.urls.static import static
from django.conf import settings

# from . import views
from .viewsets import uploadView,PostViewSet
urlpatterns =[
    # path('',uploadView, name="post_list"),
    path("upload/", uploadView, name="upload"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)