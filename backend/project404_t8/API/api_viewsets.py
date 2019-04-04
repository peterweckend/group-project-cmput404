import json
from collections import OrderedDict
from random import uniform

import dateutil.parser as parser

import API.constants as constants
import API.services as Services
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import DeleteView, UpdateView
from markdownx.utils import markdownify
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import (APIException, MethodNotAllowed,
                                       NotFound, ParseError, PermissionDenied)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser
import API.serverMethods as ServerMethods
from .forms import EditProfileForm, commentForm, friendRequestForm, uploadForm
from .models import (Comment, Follow, Friendship, Post, PostAuthorizedAuthor,
                     PostCategory, Server)
from .serializers import (CommentSerializer, FollowSerializer,
                          FriendshipSerializer, PostAuthorizedAuthorSerializer,
                          PostCategorySerializer, PostSerializer,
                          ServerSerializer, UserSerializer)

### Helper methods ###
# To help get data, and so we don't have to reuse code all the time
# What is request though in this context
# Rather, we might need to work around

# My biggest fear with these helper functions rn is how
# I'm modifying and accessing the request.path
# which makes it a new object or something
# IDK what it actually is doing, and I assume it is bad practice
# but as long as hostname information isnt lost along the way
# and security isn't compromised we should be good 

# Get author info
# extra is a boolean that returns list of friends as well as github,bio,etc.
# pk is the authors ID
# in theory, githubRequired shouldn't be true if extra is true
def getAuthorData(request, extra=False, pk=None, githubRequired=False):
    
    queryset = CustomUser.objects.all()
    user = get_object_or_404(queryset, pk=pk)
    response = {}

    request_path = "/author/" + str(pk)

    # So if the url is not blank, return what is stored
    if Services.isNotBlank(user.url):
        response["url"] = user.url
        response["id"] = user.url
    # If it is blank, do what was done before, defaulting to where it is currently hosted (local/live)
    else:
        response["id"] = "https://" + request.get_host() + request_path
        response["url"] = response["id"]

    if Services.isNotBlank(user.host):
        response["host"] = user.host
    else:
        response["host"] = "https://" + request.get_host() + "/"

    response["displayName"] = user.displayname
    
    if githubRequired:
        response["github"] = user.github_url

    # build a list of friends for the response
    # This will be optional
    if extra:
        friends_list = []
        friends = Friendship.objects.filter(friend_a=user.id)
        for friend in friends:
            friend_entry = {}

            url = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
            friend_object = get_object_or_404(queryset, pk=friend.friend_b.id)

            friend_entry["id"] = url
            # todo: look up the user, find what host they belong to, and return that value
            # instead of using request.get_host() here
            friend_entry["host"] = "https://" + request.get_host()
            friend_entry["displayName"] =  friend_object.displayname
            friend_entry["url"] = url
            friends_list.append(friend_entry)
        response["friends"] = friends_list

        # Optional info will also only be given if extra is selected
        if Services.isNotBlank(user.github_url):
            response["github"] = user.github_url
        if Services.isNotBlank(user.first_name):
            response["firstName"] = user.first_name
        if Services.isNotBlank(user.last_name):
            response["lastName"] = user.last_name
        if Services.isNotBlank(user.email):
            response["email"] = user.email
        if Services.isNotBlank(user.bio):
            response["bio"] = user.bio
    
    return response

# Get comment information
# pk is the comment ID
def getCommentData(request, pk=None):

    queryset = Comment.objects.filter(pk=pk)#.order_by('-datetime')
    comment = CommentSerializer(queryset, many=True).data[0]
    
    response = OrderedDict()

    author_id = comment["author"]
    author_response = getAuthorData(request, extra=False, pk=author_id, githubRequired=True)
    response.update({"author":author_response})
    response.update({"comment":comment["body"]})
    if comment["is_markdown"]:
        response.update({"contentType":"text/markdown"}) 
    else:
        response.update({"contentType":"text/plain"}) 
    published = parser.parse(comment["datetime"]) # ISO 8601 format
    response.update({"published":published.isoformat()})
    response.update({"id":pk})

    return response

# Get post information for a single post
# pk is the post ID
def getPostData(request, pk=None):

    # permission_classes = (IsAuthenticated,)
    queryset = Post.objects.filter(pk=pk)#.order_by('-published')
    post = PostSerializer(queryset, many=True).data[0]
    
    # Init the returned dictionary
    currentPost = OrderedDict()

    # title
    title = post["title"]
    currentPost.update({"title":title})

    # get source and origin
    # source
    source = request.scheme + "://" + str(request.META["HTTP_HOST"]) + "/posts/" + str(post["id"])
    currentPost.update({"source":source})

    # origin
    # just the path of the post
    if Services.isNotBlank(post["original_host"]):
        origin = str(post["original_host"]) + "/posts/" + str(post["id"])
    else:
        queryset = Server.objects.filter(username=constants.LOCAL_USERNAME)
        server = ServerSerializer(queryset, many=True).data[0]
        origin = server["host"] + "/posts/" + str(post["id"])
    currentPost.update({"origin":origin})

    # description
    currentPost.update({"description":post["description"]})

    # contentType
    # for now just returning markdown or plaintext, 
    # not sure how to do the other stuff
    if post["is_markdown"]:
        currentPost.update({"contentType":"text/markdown"})
    else:
        currentPost.update({"contentType":"text/plain"})

    # content
    content = post["body"]
    currentPost.update({"content":content})

    # Get author information
    # Then add author to the dic
    authorId = str(post["author"])
    author = getAuthorData(request, extra=False, pk=authorId, githubRequired=True)
    currentPost.update({"author":author})

    # categories
    post_categories = []
    queryset = PostCategory.objects.filter(post_id=post["id"])
    for category in queryset:
        post_categories.append(category.category)
    
    currentPost.update({"categories":post_categories})
    
    # Get comment info

    # TODO: add the total number of comments, and page size, and next, 
    # previous, and all that other pagination stuff here

    # TODO peter you should be able to figure this out
    # Use the helper function you will make
    # This actually looks so tedious omg
    # From spec:
    # You should return ~ 5 comments per post.
	# should be sorted newest(first) to oldest(last)
    comments_response = []
    queryset = Comment.objects.filter(post=pk).order_by('-datetime')
    comments = CommentSerializer(queryset, many=True).data
    # get only 5 most recent comments
    comments = comments[:5]
    
    for comment in comments:
        comments_response.append(getCommentData(request, pk=comment["id"]))
    currentPost.update({"comments":comments_response})

    published = parser.parse(post["published"]) # ISO 8601 format
    currentPost.update({"published":published.isoformat()})

    currentPost.update({"id":post["id"]})
    
    # visibility ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
    currentPost.update({"visibility":Services.get_privacy_string_for_post(post["privacy_setting"])})

    authorized_authors = []
    queryset = PostAuthorizedAuthor.objects.filter(post_id=post["id"])
    for author_post_object in queryset:
        authorized_authors.append(author_post_object.authorized_author.get_url_to_author())    
    currentPost.update({"visibleTo":authorized_authors})

    currentPost.update({"unlisted":post["is_unlisted"]})
    
    return currentPost

# returns the X-User header's author ID if present
# otherwise returns the authenticated user
# otherwise returns None
def getAuthorIdForApiRequest(request):
    # check if X-User header exists
    if 'HTTP_X_USER' in request.META:
        author_url = request.META['HTTP_X_USER']
        author_split = author_url.split("/author/")
        if len(author_split) == 2:
            return author_split[1]
        else:
            return None
    # check if auth information sent in
    elif not isinstance(request.user, AnonymousUser):
        try:
            author = CustomUser.objects.get(username=request.user)
            return author.id
        except:
            return None
    else:
        return None


############ API Methods

class PostsPagination(PageNumberPagination):
    page_size = 50
    #  allows the client to set the page size on a per-request basis
    page_size_query_param = 'size'
  
# https://www.django-rest-framework.org/api-guide/routers/
# https://www.django-rest-framework.org/api-guide/viewsets/#api-reference

class PostsViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post'] # only GETs allowed right now
    queryset = Post.objects.filter()
    pagination_class = PostsPagination
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    # Instantiates and returns the list of permissions that this view requires.
    # This is useful if you only want some Posts URLs to require authentication but not others
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = []
    #     else:
    #         permission_classes = [IsAuthenticated]
    #     return [permission() for permission in permission_classes]

    # GET http://service/posts (all posts marked as public on the server)
    # Ok, this is gonna get real fucking nasty so read carefully
    # NVM, we are gonna modularize it
    def list(self, request):
        
        # Query <all> amount of public posts from the table
        # This can be done with django pagination framework somehow
        # But that can just be done later >:)
        # TODO Pagination shit here somehow
        queryset = Post.objects.filter(privacy_setting="6").order_by('-published')
        paginator = PostsPagination()
        public_posts = paginator.paginate_queryset(queryset, request)
            
        # This serializes all the posts into an ordered dictionary
        # Hopefully only the amount requested
        serialized_posts = PostSerializer(public_posts, many=True)

        # We don't want to use this one, the order is all messed up and shit
        # Although in theory the order shouldn't matter if they 
        # use a proper json parser
        # Anyways, we will create a new ordered dict
        # And make sure all the correct elements are added in order
        
        # Response is the bigboy json response at the end
        response = OrderedDict()

        # First is the meta data
        # "query":"posts"
        response.update({"query":"posts"})

        # count
        count = len(queryset)
        response.update({"count":count})

        # size
        # This is the size of what was requested
        # Default can be 50 for now or something
        response.update({"size":Services.get_page_size(request, paginator)})
        
        # next
        if paginator.get_next_link() is not None:
            response.update({"next":paginator.get_next_link()})
        else: 
            response.update({"next":None})

        # previous
        if paginator.get_previous_link() is not None:
            response.update({"previous":paginator.get_previous_link()})
        else: 
            response.update({"previous":None})

        # posts
        # loop through the retrieved posts (currently all of them)
        # and harness the data like a madman
        posts = []
        
        for post in serialized_posts.data:
            # Get single post information
            postId = str(post["id"])            
            posts.append(getPostData(request, pk=postId))

        # response.update({"posts":serialized_posts.data})
        response.update({"posts":posts})
    
        # Finally, return this huge mfer
        return Response(response)
    
    # GET http://service/posts/{POST_ID} access to a single post with id = {POST_ID}
    def retrieve(self, request, pk=None):
        # permission_classes = (IsAuthenticated,)
        queryset = Post.objects.filter(pk=pk)
        # serializer_class = PostSerializer(queryset, many=True)
        post = getPostData(request, pk=pk)
        response = OrderedDict()
        response.update({"query":"getPost"})
        response.update({"posts":post})
        

        # return Response(serializer_class.data)
        return Response(response)
    
    # the API endpoint accessible at GET http://service/posts/{post_id}/comments
    @action(methods=['get','post'], detail=True, url_path="comments")
    def userPostComments(self, request, pk=None):
        permission_classes = (IsAuthenticated,)
        post_id = pk
        
        # does the post exist?
        try:
            requested_post = Post.objects.get(id=post_id)
        except:
            response = {
                'query': 'addComment',
                    'success':False,
                    'message':"Comment not allowed"
            }
            return Response(response, status=403)

        if request.method == "POST":
            # check that we're allowed to see the post - for now just check if the posts are public
            # for right now, just return comments from public posts
            # should we check if post visibility is serveronly/private?
            request_user_id = getAuthorIdForApiRequest(request)
            if request_user_id == None:
                raise ParseError("No correct X-User header or authentication were provided.")

            if Services.has_permission_to_see_post(request_user_id, requested_post): 
                body = json.loads(request.body.decode('utf-8'))
                author = body["comment"]["author"]
                commentID = body["comment"]["id"]
                comment = body["comment"]["comment"]
                postTime = body["comment"]["published"]
                post = Post.objects.get(pk=post_id)

                # swapped to UUID so this shouldn't be an issue 
                # if Comment.objects.get(pk=commentID):
                #     response = {
                #     'query': 'addComment',
                #         'success':False,
                #         'message':"Comment not allowed"
                #     }
                #     return Response(response, status=403)

                Services.addAuthor(author)

                newComment = Comment(id=commentID, author=author, post=post, datetime=postTime, body=comment)
                newComment.save()
                response = {
                    'query': 'addComment',
                        'success':True,
                        'message':"Comment Added"
                }
                return Response(response, status=200)
            else:
                response = {
                    'query': 'addComment',
                        'success':False,
                        'message':"Comment not allowed"
                }
                return Response(response, status=403)

        elif request.method == "GET": # this handles "GET" methods
            # check that we're allowed to see the post - for now just check if the posts are public
            # for right now, just return comments from public posts
            paginator = PostsPagination()
            # if requested_post.privacy_setting == "6": 
            request_user_id = getAuthorIdForApiRequest(request)
            if request_user_id == None:
                raise ParseError("No correct X-User header or authentication were provided.")

            if Services.has_permission_to_see_post(request_user_id, requested_post): 
                queryset = Comment.objects.filter(post=pk).order_by('-datetime')
                comments = CommentSerializer(queryset, many=True).data
                comments_response = []
                
                for comment in comments:
                    comments_response.append(getCommentData(request, pk=comment["id"]))

                paginated_comments = paginator.paginate_queryset(comments_response, request)

                response = OrderedDict()
                response.update({"query":"comments"})
                response.update({"count": len(queryset)})
                response.update({"size": Services.get_page_size(request, paginator)})
                response.update({"next": None})
                response.update({"previous": None})
                response.update({"comments":paginated_comments})

                if paginator.get_next_link() is not None:
                    response["next"] = paginator.get_next_link()
                if paginator.get_previous_link() is not None:
                    response["previous"] = paginator.get_previous_link()

                return Response(response)
            else: 
                raise PermissionDenied("Forbidden: You don't have permission to access comments for this post or you provided an invalid user.")
        else: 
            raise MethodNotAllowed(method=request.method)

class FriendRequestViewSet(viewsets.ModelViewSet):
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.filter()
    serializer_class = UserSerializer

    # POST to service/friendrequest
    # This is the only functionality here
    # @action(methods=['post'], detail=True, url_path="friendrequest/")
    # Should this allow unathenticated users??
    def create(self, request):
        if request.method == "POST":
            # extract the author and receiver IDs
            body = json.loads(request.body.decode('utf-8'))

            author = body["author"]
            friend = body["friend"]["id"].split("/")[-1]

            # This should be done better, but right now
            # we are gonna get the username using the id
            # and then handle the friendrequest

            # If the sender ID or the receiver ID do not exist still just 200 them
            # If the author doesn't exist create a foregin account for them on connectify
            Services.addAuthor(author)

            # If the receiver doesn't exist do nothing
            try:
                friend = CustomUser.objects.get(pk=friend)
            except:
                return Response(status=200)

            Services.handle_friend_request(friend, author)
        # handleFriendRequest
        return Response(status=200)

    # http://service/friendrequest/processRequest
    @action(methods=['post'], detail=False)
    def processRequest(self, request, pk=None):
        body = request.data
        idOfFriendToAddOrDeny = body["IdOfFriendToAddOrDeny"]
        idOfLoggedInUser = body["IdOfLoggedInUser"]
        action = body["action"]
        
        friendToAddOrDeny = CustomUser.objects.get(pk=idOfFriendToAddOrDeny)
        loggedInUser = CustomUser.objects.get(pk=idOfLoggedInUser)

        if action == "ACCEPT":
            requesterIsRemote = False
            if Services.isNotBlank(friendToAddOrDeny.host):
                requesterIsRemote = True

            if requesterIsRemote:
                result = ServerMethods.befriend_remote_author_by_id(idOfFriendToAddOrDeny, idOfLoggedInUser)
            else:
                Services.handle_friend_request(idOfFriendToAddOrDeny, idOfLoggedInUser)

        else:
            follow = Follow.objects.get(follower=idOfFriendToAddOrDeny, receiver=idOfLoggedInUser)
            follow.delete()
            Services.updateNotificationsById(idOfFriendToAddOrDeny.id)
            Services.updateNotificationsById(idOfLoggedInUser.id)
            
        return Response(status=200)
    

class AuthorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.filter()
    pagination_class = PostsPagination
    serializer_class = UserSerializer

    # we don't want there to be any functionality for GET http://service/author 
    def list(self, request):
        raise NotFound()

    # we don't want there to be any functionality for GET http://service/author
    def create(self, request):
        raise NotFound()

    # GET http://service/author/{author_id}
    # returns information about the author
    def retrieve(self, request, pk=None):
        return Response(getAuthorData(request, extra=True, pk=pk, githubRequired=False))
    

    # http://service/author/posts (posts that are visible to the currently authenticated user)
    @action(methods=['get'], detail=False)
    def posts(self, request, pk=None):
        # uname = request.user
        # uid = uname.id
        uid = getAuthorIdForApiRequest(request)
        if uid == None:
            raise ParseError("No correct X-User header or authentication were provided.")
        uid = str(uid).replace('-','')
        
        # todo: properly escape this using https://docs.djangoproject.com/en/1.9/topics/db/sql/#passing-parameters-into-raw
        # allowed_posts = Post.objects.raw(' \
        # WITH posts AS (SELECT id FROM API_post WHERE author_id in  \
        # (SELECT f2.friend_a_id AS fofid \
        #     FROM API_friendship f \
        #     JOIN API_friendship f2 ON f.friend_a_id = f2.friend_b_id \
        #     WHERE fofid NOT IN (SELECT friend_a_ID FROM API_friendship  \
        #     WHERE friend_b_id = %s) AND f.friend_b_id = %s AND fofid != %s) AND privacy_setting = 4 \
        # UNION \
        #     SELECT id FROM API_post WHERE (author_id in  \
        #     (WITH friends(fid) AS (SELECT friend_b_id FROM API_friendship WHERE friend_a_id=%s) \
        #     SELECT * FROM friends WHERE fid != %s GROUP BY fid)  \
        #     AND (privacy_setting = 3 OR privacy_setting = 4)) OR author_id = %s OR  privacy_setting = 6) \
        #     SELECT * FROM API_post WHERE id in posts \
        #     ORDER BY published DESC' , [str(uid)]*6)
        allowed_posts = []
        allPosts = Post.objects.filter().order_by('-published') # I think this returns them all

        request_user_id = getAuthorIdForApiRequest(request)
        if request_user_id == None:
            raise ParseError("No correct X-User header or authentication were provided.")

        for post in allPosts:
            if Services.has_permission_to_see_post(request_user_id, post):
                allowed_posts.append(post)

        paginator = PostsPagination()
        paginated_posts = paginator.paginate_queryset(allowed_posts, request)
        serialized_posts = PostSerializer(paginated_posts, many=True)

        response = OrderedDict()
        response.update({"query":"posts"})
        response.update({"count": len(allowed_posts)})
        response.update({"size": Services.get_page_size(request, paginator)})
        response.update({"next": None})
        response.update({"previous": None})

        posts = []
        
        for post in serialized_posts.data:
            # Get single post information
            postId = str(post["id"])            
            posts.append(getPostData(request, pk=postId))

        response.update({"posts":posts})

        if paginator.get_next_link() is not None:
            response["next"] = paginator.get_next_link()
        if paginator.get_previous_link() is not None:
            response["previous"] = paginator.get_previous_link()
        return Response(response)    

    # the API endpoint accessible at GET http://service/author/{author_id}/posts
    # Can't name this method "posts" because there's already a "posts" method above
    # so I had to add this @action tag stuff
    @action(methods=['get'], detail=True, url_path="posts")
    def userPosts(self, request, pk=None):
        author_id = self.kwargs['pk']
        author_id = str(author_id)
        # uname = request.user
        # uid = uname.id
        uid = getAuthorIdForApiRequest(request)
        if uid == None:
            raise ParseError("No correct X-User header or authentication were provided.")
        uid = str(uid)
        
        # allowed_posts = Post.objects.raw(' \
        # WITH posts AS (SELECT id FROM API_post WHERE author_id in  \
        # (SELECT f2.friend_a_id AS fofid \
        #     FROM API_friendship f \
        #     JOIN API_friendship f2 ON f.friend_a_id = f2.friend_b_id \
        #     WHERE fofid NOT IN (SELECT friend_a_ID FROM API_friendship  \
        #     WHERE friend_b_id = %s) AND f.friend_b_id = %s AND fofid != %s) AND privacy_setting = 4 \
        # UNION \
        #     SELECT id FROM API_post WHERE (author_id in  \
        #     (WITH friends(fid) AS (SELECT friend_b_id FROM API_friendship WHERE friend_a_id=%s) \
        #     SELECT * FROM friends WHERE fid != %s GROUP BY fid)  \
        #     AND (privacy_setting = 3 OR privacy_setting = 4)) OR author_id = %s OR  privacy_setting = 6) \
        #     SELECT * FROM API_post WHERE id in posts \
        #     AND author_id = %s \
        #     ORDER BY published DESC', [str(uid)]*6 + [author_id])

        # Instead of this big boy query, just query for all our posts
        # Then for each post, check to see if the user has permission
        allowed_posts = []
        allPosts = Post.objects.filter(author=author_id).order_by('-published') # I think this returns them all
        for post in allPosts:
            if Services.has_permission_to_see_post(uid, post):
                allowed_posts.append(post)


        paginator = PostsPagination()
        paginated_posts = paginator.paginate_queryset(allowed_posts, request)
        serialized_posts = PostSerializer(paginated_posts, many=True)

        response = OrderedDict()
        response.update({"query":"posts"})
        response.update({"count": len(allowed_posts)})
        response.update({"size": Services.get_page_size(request, paginator)})
        response.update({"next": None})
        response.update({"previous": None})
        # response.update({"posts": serialized_posts.data})

        posts = []
        
        for post in serialized_posts.data:
            # Get single post information
            postId = str(post["id"])            
            posts.append(getPostData(request, pk=postId))

        # response.update({"posts":serialized_posts.data})
        response.update({"posts":posts})

        if paginator.get_next_link() is not None:
            response["next"] = paginator.get_next_link()
        if paginator.get_previous_link() is not None:
            response["previous"] = paginator.get_previous_link()
        return Response(response)

    # the API endpoint accessible at GET http://service/author/<authorid>/friends/
    # returns the author's friend list
    # Also allows for POST
    # returns the list with non friends removed
    @action(methods=['get', 'post'], detail=True, url_path="friends")
    def userFriends(self, request, pk=None):

        if request.method == "POST":

            # The incoming request should have a json body
            body = json.loads(request.body)

            author_id = body["author"]

            # For each author provided, check to see if they are friends
            friends = []
            for author in body["authors"]:
                friend = friendsHelperFunction(request, author_id, author.split("/")[-1])
                if friend:
                    friends.append(author)

            body["authors"] = friends


            return Response(body)

        if request.method == "GET":
            author_id = pk
            # since the friendship table is 2-way, request a list of users whose 
            # IDs are in the friendship table, not including the author
            # make sure to format this the appropriate way
            friendship_authors = []
            friends = Friendship.objects.filter(friend_a=author_id)
            
            for friend in friends:
                url = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
                friendship_authors.append(url)
        
            # serialize friendship_authors here
            friendship_dict = {}
            friendship_dict["query"] = "friends"
            friendship_dict["author"] = pk
            friendship_dict["authors"] = friendship_authors
        
            # return serialized friendship_authors
            return Response(friendship_dict)

    @action(methods=['get'], detail=True, url_path="friends/(?P<author_id2>\d+)")
    def friends(self, request, pk=None,author_id2=None):
        author_id = pk
                # since the friendship table is 2-way, request a list of users whose 
        # IDs are in the friendship table, not including the author
        # make sure to format this the appropriate way
        if request.method == "GET":
            friendship_authors = []
            friends = Friendship.objects.filter(friend_a=author_id, friend_b=author_id2)
            friendship_dict = {}
            if friends:
                for friend in friends:
                    url = "https://" + request.get_host() + "/author/" + str(friend.friend_a.id) 
                    url2 = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
                    friendship_authors.append(url)
                    friendship_authors.append(url2)
                friendship_dict["friends"]= True
            else:
                for friend in friends:
                    url = "https://" + request.get_host() + "/author/" + str(friend.friend_a.id) 
                    url2 = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
                    friendship_authors.append(url)
                    friendship_authors.append(url2)
                
                friendship_dict["friends"]= False
        
            # serialize friendship_authors here
            friendship_dict["query"] = "friends"
            friendship_dict["authors"] = friendship_authors

            return Response(friendship_dict)
            
        else: 
             friends = Friendship.objects.filter(friend_a=author_id)

# This tells you whether 2 people are friends or not
def friendsHelperFunction(request, pk=None, author_id2=None):
    author_id = pk
    friendship_authors = []
    friends = Friendship.objects.filter(friend_a=author_id, friend_b=author_id2)
    friendship_dict = {}
    if friends:
        for friend in friends:
            url = "https://" + request.get_host() + "/author/" + str(friend.friend_a.id) 
            url2 = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
            friendship_authors.append(url)
            friendship_authors.append(url2)
        friendship_dict["friends"]= True
    else:
        for friend in friends:
            url = "https://" + request.get_host() + "/author/" + str(friend.friend_a.id) 
            url2 = "https://" + request.get_host() + "/author/" + str(friend.friend_b.id) 
            friendship_authors.append(url)
            friendship_authors.append(url2)

    if friendship_authors != []:
        # Return the url of the second ID
        return True

    return False
