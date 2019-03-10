from django.shortcuts import render
from rest_framework import generics,status,viewsets
from .models import Posts
from .serializers import PostsSerializer

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .serializers import *
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
# Create your views here.
from django.http import JsonResponse
def names(request):
    return JsonResponse({'names':['Will','Rod','GRANT']})

# index_view = never_cache(TemplateView.as_view(template_name='home.html'))
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
    #
    # elif request.method == 'POST':
    #     serializer = PostsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
