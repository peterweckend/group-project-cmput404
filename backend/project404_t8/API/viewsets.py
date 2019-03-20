from django.shortcuts import render
from rest_framework import generics,status,viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Post, Comment, Friendship, Follow, Server
from .serializers import UserSerializer, PostSerializer, CommentSerializer, FriendshipSerializer, FollowSerializer, ServerSerializer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from .forms import uploadForm, friendRequestForm,commentForm
from django.conf import settings
from users.models import CustomUser
from random import uniform
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
import API.services as Services

# Token and Session Authetntication: https://youtu.be/PFcnQbOfbUU
# Django REST API Tutorial: Filtering System - https://youtu.be/s9V9F9Jtj7Q

class UserViewSet(viewsets.ModelViewSet):
        queryset = CustomUser.objects.all()
        serializer_class = UserSerializer

        @action(methods=['get'], detail=False)
        def newest(self, request):
            newest = self.get_queryset().order_by('id').last()
            serializer = self.get_serializer_class()(newest)
            return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

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
    # So if we wanted to get even more fancy too, ajax could post to this itself and we
    # wouldnt require another page, but lets just take babysteps for now
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = uploadForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # So models could just expect a dictionary of these values
            # How do we know what user is posting the data?
            # something like this: request.user.id 
            # Probably just add that to the form.cleaned_data dictionary
            
            newPost = form.cleaned_data
            # print(newPost)
            # print(request.FILES)
            # Don't do anything if no image is uploaded
            newPost["imageLink"] = None
            if request.FILES != {}:
                newPost["imageLink"] = request.FILES["imageLink"]

            # If shared author isn't input then convert it to None/null for now 
            if newPost["sharedAuthor"] == "":
                newPost["sharedAuthor"] = None

            newPost = Post(
                author = request.user,
                title = newPost["title"],
                body = newPost["body"],
                image_link = newPost["imageLink"],
                privacy_setting = newPost["privacy"],
                shared_author = newPost["sharedAuthor"],
                is_markdown = newPost["markdown"]
            )

            # print(newPost)
            newPost.save()
            id = newPost.id

            # redirect to a new URL:
            return HttpResponseRedirect('/post/%s' %id)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = uploadForm()

    return render(request, 'upload/upload.html', {'form': form})

def postView(request, id):

    # We could check to see if the user has permission to view this post in here
    # Based on the privacy setting etc.

    # This is our post object with the given ID
    # If the post doesn't exist it instantly 404's
    # This way we won't have to do any taxing database math
    post = get_object_or_404(Post, pk=id) #pk is primary key
    
    # Do not display an image if the image does not exist
    imageExists = False
    if post.image_link != "":
        imageExists = True
    
    # Perform privacy calculations
    # Has permission will be passed in
    # If its False we could either display a 404 or a "you do not have permission"
    requesting_user_id = request.user.id
    hasPermission = Services.has_permission_to_see_post(requesting_user_id, post)

    post.title = "OVERWRIDDEN"

    # Post is the post data
    # imageExists is whether or not there is an image to display
    # Has permission determines whether or not to display content to the user
    return render(request, 'post/post.html', {
        "post":post,
        "imageExists":imageExists,
        "hasPermission":hasPermission
        })

def friendRequestView(request):
    # When the user posts here, they will send a follow/friend request
    # This will add an element to follow or something maybe?
    # So I think this should all be done through ajax too to be honest
    # So on the profile page when you click the button it just sends the 
    # http request using AJAX instead of the browser

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = friendRequestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # Send the friend request

            # Uncomment this code to add 10 friends to the currently logged in user
            # You cant login to these accounts though lol
            # 
            # for i in range(10):
            #     newUser = CustomUser(username=uniform(1,10),password=uniform(1,10))
            #     newUser.save()
            #     friend = Friendship(friend_a=request.user, friend_b=newUser)
            #     friend.save()
            
            receiver_username = form.cleaned_data["friendToAdd"]
            receiver_username = CustomUser.objects.get(username=receiver_username)
            follower_username = request.user

            if receiver_username == follower_username:
                # just return a redirect for now
                return HttpResponseRedirect('/')

            # not yet functionality to prevent multiple requests in a row

            Services.handle_friend_request(receiver_username, follower_username)

            # redirect to a new URL: homepage
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = friendRequestForm()

    return render(request, 'friendrequest/friendrequest.html', {'form': form})

def profileView(request, username):
    # LoginRequiredMixin
    # login_url: ''
    user = CustomUser.objects.get(username=username)
    profile_posts = Post.objects.filter(author=request.user.id)
    return render(request, 'profile/profile.html', {'user':user, "posts":profile_posts})

def homeListView(request):

    # this try and except is to render posts into homepage
    try:
        uname = request.user
        uid = uname.id
        post = Post.objects.raw(' \
        WITH posts AS (SELECT id FROM API_post WHERE author_id in  \
        (SELECT f2.friend_a_id AS fofid \
            FROM API_friendship f \
            JOIN API_friendship f2 ON f.friend_a_id = f2.friend_b_id \
            WHERE fofid NOT IN (SELECT friend_a_ID FROM API_friendship  \
            WHERE friend_b_id = %s) AND f.friend_b_id = %s AND fofid != %s) AND privacy_setting = 4 \
        UNION \
            SELECT id FROM API_post WHERE (author_id in  \
            (WITH friends(fid) AS (SELECT friend_b_id FROM API_friendship WHERE friend_a_id=%s) \
            SELECT * FROM friends WHERE fid != %s GROUP BY fid)  \
            AND (privacy_setting = 3 OR privacy_setting = 4)) OR author_id = %s OR  privacy_setting = 6) \
            SELECT * FROM API_post WHERE id in posts', [int(uid)]*6)
    except:
        post = Post.objects.all()
    #     # Do not display an image if the image does not exist
    # imageExists = False
    # if post.image_link != "":
    #     imageExists = True

    # get the user and friends and pass it to homepage
    # user = CustomUser.objects.get(username=request.user)
    friend = Friendship.objects.all()


    
    
    # Only pass in post and friends if they aren't none
    # If they are we cannot pass them in{"post":post,"":friend}
    pageVariables = {}
    
    # Check to see if any posts exist
    try:
        post[0]
        pageVariables["post"] = post
    except:
        # The raw query set returns no post, so do not pass in any post to the html
        pass
    if friend:
        pageVariables["friend"] = friend

    return render(request, 'homepage/home.html', pageVariables)


class PostDelete(DeleteView):
    model = Post
    success_url= reverse_lazy("home")

    template_name= 'delete/delete_post.html'
# class PostEdit(UpdateView):
#     template_name = "home.html"
#     model = Post
#     form_class= HomeForm
class FriendDelete(DeleteView):
    model = Friendship
    success_url= reverse_lazy("home")

    template_name= 'delete/delete_friend.html'
    # overrided delete function so that not only will it delete the user who requests the friend deletion
    # but also will delete the friendship on other user side

    # how to delete stuff
    # burhan Khalid
    # https://stackoverflow.com/questions/12796870/how-does-django-delete-the-object-from-a-view
    # rudra
    # https://stackoverflow.com/questions/30747075/django-class-based-delete-view-and-validation
    def delete (self,request, *args, **kwargs):
       self.object= self.get_object()
       
       Friendship.objects.filter(friend_a=self.object.friend_b, friend_b=self.object.friend_a ).delete()

       self.object.delete() 
       return HttpResponseRedirect(self.success_url)
def comment_thread(request,pk):
    post = get_object_or_404(Post,pk =pk)
    if request.method =='POST':
        # pass
        form = commentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            # newPost = Post(
            #     author = request.user,
            #     title = newPost["title"],
            #     body = newPost["body"],
            #     image_link = newPost["imageLink"],
            #     privacy_setting = newPost["privacy"],
            #     shared_author = newPost["sharedAuthor"],
            #     is_markdown = newPost["markdown"]
            # )
            comment.post = post
            comment.author = request.user
            comment.save()
            return HttpResponseRedirect('/')
    else:
        form =commentForm()
    template = "comments/comment_thread.html"
    context = {'form':form}
    return render(request,template,context)