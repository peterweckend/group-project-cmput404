from django.shortcuts import render
from rest_framework import generics,status,viewsets
from .models import Posts
from .serializers import PostsSerializer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import uploadForm
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
    #
    # elif request.method == 'POST':
    #     serializer = PostsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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