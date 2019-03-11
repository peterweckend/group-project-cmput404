from django.shortcuts import render
from rest_framework import generics,status,viewsets
from .models import Posts
from .serializers import PostsSerializer
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .serializers import *

# Create your views here.
#@api_view(['GET','POST'])
class PostViewSet(viewsets.ModelViewSet):
    """
    Provides a get method handler.
    """
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

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
