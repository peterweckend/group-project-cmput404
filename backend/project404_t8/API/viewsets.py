from django.shortcuts import render
from rest_framework import generics,status,viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Post, Comment, Friendship, Follow, Server
from .serializers import UserSerializer, PostSerializer, CommentSerializer, FriendshipSerializer, FollowSerializer, ServerSerializer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import uploadForm
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .serializers import *

# Token and Seesion Authetntication: https://youtu.be/PFcnQbOfbUU
# Django REST API Tutorial: Filtering System - https://youtu.be/s9V9F9Jtj7Q

# Create your views here.
#@api_view(['GET','POST'])

class UserViewSet(viewsets.ViewSet): #this makes it so when you go to localhost/user/, you can't post
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

# get newest value for user
# class UserViewSet(viewsets.ModelViewSet):
#         queryset = User.objects.all()
#         serializer_class = UserSerializer

#         @action(methods=['get'], detail=False)
#         def newest(self, request):
#             newest = self.get_queryset().order_by('id').last()
#             serializer = self.get_serializer_class()(newest)
#             return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    """
    Provides a get method handler.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # if request.method == 'GET':
    #     queryset = Posts.objects.all()
    #     serializer = PostsSerializer(queryset, many=True)
    #     return Response(serializer.data)
    
    # elif request.method == 'POST':
    #     serializer = PostsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

def uploadView(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = uploadForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # Here is 
            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = uploadForm()

    return render(request, 'upload/upload.html', {'form': form})