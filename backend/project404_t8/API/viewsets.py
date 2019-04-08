from django.shortcuts import render
from rest_framework import generics,status,viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.html import strip_tags,escape
from .models import Post, Comment, Friendship, Follow, Server, PostAuthorizedAuthor
from users.models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, PostSerializer, CommentSerializer, FriendshipSerializer, FollowSerializer, ServerSerializer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from .forms import uploadForm, friendRequestForm, EditProfileForm, commentForm, updatePostForm
from django.conf import settings
from users.models import CustomUser
from random import uniform
import json
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
import API.services as Services
from rest_framework.exceptions import APIException, MethodNotAllowed, NotFound, PermissionDenied
from markdownx.utils import markdownify
from .api_viewsets import PostsViewSet, AuthorViewSet, FriendRequestViewSet
from .serverMethods import befriend_remote_author_by_id, get_remote_posts_for_feed, get_user, get_remote_comments_by_post_id
from django.db.models import Q
import requests


# Token and Session Authetntication: https://youtu.be/PFcnQbOfbUU
# Django REST API Tutorial: Filtering System - https://youtu.be/s9V9F9Jtj7Q

def uploadView(request):
    if request.method == 'POST':
        author = request.user
        title = request.POST.get('title')
        # Escape if they have script in it
        # Otherwise don't escape it and let whatever happens happen
        body = request.POST.get('body')
        if "<script>" in body or "</script>" in body:
            body = escape(body)  

        image_link = request.POST.get('imageLink')
        privacy_setting = request.POST.get('privacy')
        shared_authors = request.POST.get('sharedAuthor')
        is_markdown = request.POST.get('markdown')
        is_unlisted = request.POST.get('unlisted')

        # Check if there's an image
        if image_link == "": 
            image_link = None
        if request.FILES != {}:
            image_link = request.FILES["imageLink"]
        # Check if markdown option is selected
        if is_markdown == None:
            is_markdown = False
        elif is_markdown ==  "on":
            is_markdown = True
        # Check if unlisted option is selected
        if is_unlisted == None:
            is_unlisted = False
        elif is_unlisted ==  "on":
            is_unlisted = True

        newPost = Post(
            author = author,
            title = title,
            body = body,
            image_link = image_link,
            privacy_setting = privacy_setting,
            shared_author = None,
            is_markdown = is_markdown,
            is_unlisted = is_unlisted
        )
        newPost.save()
        id = newPost.id

        # Try to add the shared authors
        # 231312312312, 123123123123,213123123
        # Example string of UUID's
        # First split the string on Commas
        if shared_authors != "" and str(privacy_setting) == '2':
            shared_authors = shared_authors.replace(" ", "").split(',')

            # Should now have a list of UUID's
            # For each UUID, try to add them to the table postAuthorizedAuthor
            for shared_author in shared_authors:
                # print(shared_author)
                try:
                    
                    author = CustomUser.objects.get(pk=shared_author)

                    new = PostAuthorizedAuthor(
                        post_id = newPost,
                        authorized_author = author
                    )
                    new.save()
                except Exception as e:
                    print(e)


        # redirect to a new URL:
        return HttpResponseRedirect('/post/%s' %id)
    else:
        pass
    
    context = {}
    return render(request, 'upload/upload.html', context)

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
    hasPermission = Services.has_permission_to_see_post(request.user.id, post)

    if post.is_markdown:
        post.body = markdownify(post.body)

    # Post is the post data
    # imageExists is whether or not there is an image to display
    # markDown is whether or not to display the plaintext or markdown contents
    # Has permission determines whether or not to display content to the user
    post.privacy_setting = Services.get_privacy_string_for_post(post.privacy_setting)
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

            # receiver_data is either a username or an id
            receiver_data = form.cleaned_data["friendToAdd"]
            follower = request.user

            # if receiver_data is a username, check its not the same as the follower's username
            if receiver_data == follower.username:
                # just return a redirect for now
                return HttpResponseRedirect('/')

            # TODO: functionality to prevent multiple requests in a row

            is_remote_author = form.cleaned_data["isRemoteAuthor"]
            if is_remote_author:
                result = befriend_remote_author_by_id(receiver_data, follower.id)
            else:
                receiver = CustomUser.objects.get(username=receiver_data)
                Services.handle_friend_request(receiver, follower)

            # redirect to a new URL: homepage
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = friendRequestForm()

    return render(request, 'friendrequest/friendrequest.html', {'form': form})

def profileView(request, username):
    author = CustomUser.objects.get(username=username)

    # will probably change the edit profile functionality later, and check if profile author == logged in user here
    # get the profile author
    if request.user.username == username:
        profile_posts = Post.objects.filter(author=author.id).order_by('-published')
    else:
        profile_posts_all = Post.objects.filter(author=author.id).order_by('-published')
        profile_posts = []
        for post in profile_posts_all:
            if Services.has_permission_to_see_post(request.user.id, post):
                profile_posts.append(post)
    for p in profile_posts:
        if p.is_markdown:
            p.body = markdownify(p.body)
    
    return render(request, 'profile/profile.html', {'author':author, "posts":profile_posts})

class PostUpdate(UpdateView):
    model = Post
    success_url= reverse_lazy("home")
    template_name= 'update/update_post.html'
    form_class = updatePostForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # print(self.object)
        return super(PostUpdate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if the profile doesn't exist, return 404, otherwise return the profile author object 
        context['post'] = get_object_or_404(Post, id=self.object.id)
        return context
    
    # update the model
    def form_valid(self, form):
        #save cleaned post data
        clean = form.cleaned_data
        self.object = form.save()
        return super(PostUpdate, self).form_valid(form)

    # redirects to homepage after successful edit 
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("home")


class editProfile(UpdateView):

    model = CustomUser
    form_class = EditProfileForm
    template_name = "editprofile/editprofile.html"  
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # print(self.object)
        return super(editProfile, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if the profile doesn't exist, return 404, otherwise return the profile author object 
        context['profile_author'] = get_object_or_404(CustomUser, id=self.object.id)
        return context
    
    # update the model
    def form_valid(self, form):
        #save cleaned post data
        clean = form.cleaned_data
        self.object = form.save()
        return super(editProfile, self).form_valid(form)

    # redirects to homepage after successful edit 
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("home")
  
def homeListView(request):
    # this try and except is to render posts into homepage
    try:
        uname = request.user
        uid = uname.id
        foreignPosts = get_remote_posts_for_feed(request.user.id)

        # ------------- set queries by Tolu ----------------------
        userUser = CustomUser.objects.filter(pk=uid)[0].id
        hostHost = CustomUser.objects.filter(pk=uid)[0].host
        option1 = Post.objects.filter(author=userUser)
        authorized_posts = PostAuthorizedAuthor.objects.filter(authorized_author = userUser).values_list('post_id', flat=True)
        option2 = Post.objects.filter(pk__in=authorized_posts)
        friendZone = Friendship.objects.filter(friend_a=userUser).values_list('friend_b', flat=True)
        fofriendZone = Friendship.objects.filter(friend_a__in=friendZone).values_list('friend_b', flat=True)
        option3 = Post.objects.filter(Q(author__in=friendZone) & Q(privacy_setting=3) | Q(author__in=friendZone) & Q(privacy_setting=4))
        option4 = Post.objects.filter(Q(author__in=fofriendZone) & Q(privacy_setting=4))
        option5 = Post.objects.filter(Q(author__in=friendZone) & Q(privacy_setting=5) &Q(original_host=hostHost))
        option6 = Post.objects.filter(Q(privacy_setting=6))
        unlistedPosts = Post.objects.filter(Q(is_unlisted=True) & ~Q(author=userUser))
        allPosts = option1.union(option2,option3,option4,option5,option6)
        if unlistedPosts.exists():
            viewable_posts = allPosts.difference(unlistedPosts).order_by('-published')
        else:
            viewable_posts = allPosts.order_by('-published')
    except:
        pass
    
    # get the user and friends and pass it to homepage
    # user = CustomUser.objects.get(username=request.user)
    friend = Friendship.objects.all()

    try:
        user = CustomUser.objects.get(username=request.user)        
        # print(user.github_id,1)
        if user.github_id != "":
            user.github_url = "https://api.github.com/users/{}/events/public".format(user.github_id)
            github_url= user.github_url
            r = requests.get(github_url)
            # print(github_url)
            print("\nRequesting:", github_url,"Status code:", r.status_code,"\n")

            if r.status_code != 200:
                print("An error occured")
                
            
            response = r.content.decode("utf-8")
            github_posts= json.loads(response)
            # print(github_posts[0],1111)
            count = 0
            
            for post in github_posts:
                # print(post["repo"]["name"])
                
                if count ==5:
                    break
                try:
                    if post["type"]== "PushEvent":
                        message= "I just pushed to my repository "+ str(post["repo"]["name"]) 
                    elif post["type"] == "CreateEvent":
                        message = "I just created "+ str(post["repo"]["name"])
                    else:
                        message= "About Github"
                        
                    if Post.objects.filter(published=post["created_at"], title="Made a post about github").exists():
                        print("has post")
                        break

                    post_object = Post( author=user, title="Made a post about github", description=post["type"], body=message, privacy_setting='6', published=post["created_at"])
                    # print(192)
                    post_object.save()
                    count +=1
                except Exception as e:
                    print(e,189) 

    except:
        pass
    
    # Only pass in post and friends if they aren't none
    # If they are we cannot pass them in{"post":post,"":friend}
    pageVariables = {}
    
    # Check to see if any posts exist
    try:
        # This will index the first result of the query
        # will crash if there are no results, taking us to except
        viewable_posts[0]

        # Now that we are here, loop through each element
        # And markdownify the body if it is_markdown
        for p in viewable_posts:
            if p.is_markdown:
                p.body = markdownify(p.body)

        pageVariables["post"] = viewable_posts
        pageVariables["postRemote"]=postRemote
    except:
        # The raw query set returns no post, so do not pass in any post to the html
        pass
    try:
        if user:
            pageVariables["friends"] = friend
  
        if friend:
            pageVariables["githubUrl"] = github_url
    except:
        pass

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


def friendsView(request):
    # This will be a list of the users friends and friend requests
    # In the future this could appear right on their profile as per the mockups
    # but for now it will exist as its own page     
    # It will also allow them to accept/ignore friend requests

    # Right now, a friend request is an unignored follow
    # So, get all the logged in users unignored follows
    requests = Follow.objects.filter(receiver=request.user.id, ignored=False)

    # Now we have the id's of all the unignored followers
    # Convert that to a list of usernames
    # We can do this by querying for each username based on the id
    requests2 = []
    for r in requests: 
        requests2.append(CustomUser.objects.get(id=r.follower_id))
    requests = requests2

    # Get the users friends
    friends1 = Friendship.objects.filter(friend_a=request.user.id)
    friends2 = Friendship.objects.filter(friend_b=request.user.id)
    friends = set()
    # alright this feels really messy but it should work I think
    # If the models change things could get cringed but I actually think its fine
    # Iterate through each queryset, and append the ids of each element to the list
    for row in friends1:
        friends.add(row.friend_b.username)
    for row in friends2:
        friends.add(row.friend_a.username)
    friends = list(friends)
    friends.sort()

    friends_obj = Friendship.objects.all()

    # Make sure None isn't being passed to the template at all
    pageVariables = {}
    if friends != {}:
        pageVariables["friends"] = friends
    if requests != []:
        pageVariables["requests"] = requests
    if friends_obj != {}:
        pageVariables["friendsObj"] = friends_obj
    

    return render(request, 'friends/friends.html', pageVariables)

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
