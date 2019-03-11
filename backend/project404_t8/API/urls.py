from django.urls import pathh
from . import views

urlpatterns =[
    path('',views.postViewSet, name="post_list")

]