from .models import Server, Post, Comment
from users.models import CustomUser
import requests
import API.services as Services
from .serializers import UserSerializer, PostSerializer, CommentSerializer, FriendshipSerializer, FollowSerializer, ServerSerializer
from django.utils import timezone
import API.constants as constants
import json

# returns a header object of the format:
# X-User: http://service/author/:uuid
# this should be included in the headers of 
# any requests that involve checking permissions

def get_custom_header_for_user(user_id):
    try:
        queryset = Server.objects.filter(username=constants.LOCAL_USERNAME)
        server = ServerSerializer(queryset, many=True).data[0]
        header = {'X-User': server["host"] + "/author/" + str(user_id)}
        return header
    except Exception as e:
        print("An error occurred generating the custom header:",e)
        return None

def get_server_info(remote_server_host):
    try:
        queryset = Server.objects.all()
        for server in queryset:
            if server.host == remote_server_host:
                return server
        return None
    except:
        return None

def get_our_server(): 
    try:
        queryset = Server.objects.all()
        for server in queryset:
            if server.username == constants.LOCAL_USERNAME:
                return server
        return None
    except:
        return None

def get_remote_author(remote_server, remote_author_id):
    request_url = remote_server.host + "/author/" + str(remote_author_id)
    # print("here",65)

    r = requests.get(request_url, auth=(remote_server.username, remote_server.password))
    # print("r",39)
    if r.status_code == 200:
        # print("hi")
        response = r.content.decode("utf-8")
        # print(response,43)
        # print(type(response))
        # print(222222222222)
        author_data= json.loads(response)
        # print(11111111111111111)
        # print(author_data["id"].split("author/")[1],22)
        try:
            remote_author = CustomUser(timestamp=timezone.now(), id=author_data["id"].split("author/")[1], host=remote_server.host, displayname=author_data["displayName"], github_url=author_data["github"], username = "gart", password= "12345", bio=author_data["bio"])
        
            # print("here",65)
        
            remote_author.save()
        except Exception as e:
            print(e,52)
        return remote_author
    else:
        return None

# returns a second parameter stating if the author is local
def get_user(remote_author_id):
    # search for any local authors with the username
    remote_author_id ="e204d9bb-73aa-41d7-aceb-b9fce475d65f"
    try:
        queryset = CustomUser.objects.filter(pk=remote_author_id)
        author = UserSerializer(queryset, many=True).data[0]
        author_is_local = True
        return author, author_is_local

    # search for any server authors with the username
    except:
        queryset = Server.objects.all()
        for server in queryset:
            author = get_remote_author(server, remote_author_id)
            if author == None:
                return None
            else:
                author_is_local = False
                return author, author_is_local
    return None



# we send friend request to a remote server
# returns False if the operation fails
def befriend_remote_author_by_id(remote_author_id, local_author_id):

    local_author, _ = get_user(local_author_id)
    if local_author == None:
        return False
    author = {}
    author["id"] = local_author.id
    author["host"] = local_author.host
    author["displayName"] = local_author.displayname
    author["url"] = local_author.url

    remote_author, author_is_local = get_user(remote_author_id)
    if remote_author == None:
        return False
    if author_is_local:
        Services.handle_friend_request(remote_author, local_author)
        return True
    friend = {}
    friend["id"] = local_author.id
    friend["host"] = local_author.host
    friend["displayName"] = local_author.displayname
    friend["url"] = local_author.url

    data = {}
    data["query"] = "friendrequest"
    data["author"] = author
    data["friend"] = friend
    # todo send to all servers?
    request_url = remote_server.host + "/author/" + str(remote_author_id)
    r = requests.post(request_url, auth=(remote_server.username, remote_server.password))
    response = r.text

    if r.status_code != 200:
        return False

    return True

# this will fetch and return all remote posts that 
# the current user is capable of seeing
# for now, this will not persist the post objects in the database
# it will just return a list of post objects
def get_remote_posts_for_feed(current_user_id):
    # skipping friend of a friend for now

    # current strategy: get all posts from all connected servers
    # go through the posts and filter out ones that the current user
    # should not be able to see
    
    #######################3 will probably have to change it right now its hardcoded as garys lol
    # current_user_id="e204d9bb-73aa-41d7-aceb-b9fce475d65f"
    ####################################
    remote_posts = []
    try:
        queryset = Server.objects.all()
        for remote_server in queryset:
            if remote_server.username == constants.LOCAL_USERNAME:
                continue

            request_url = remote_server.host + "/author/posts?size=25"
            try:
                header = get_custom_header_for_user(current_user_id)
            except Exception as e:
                print(e,52)
            r = requests.get(request_url, auth=(remote_server.username, remote_server.password), headers=header)

            print("\nRequesting:", request_url,"Status code:", r.status_code,"\n")

            if r.status_code != 200:
                print("An error occured")
                continue
            
            # print("hi")
            response = r.content.decode("utf-8")
            # print(response,43)
            # print(type(response))
            # print(222222222222)
            posts= json.loads(response)
            # print(172)
            # print(posts,11111111111111111)
            # print(posts["id"].split("author/")[1],22) # hopefully this is the correct syntax for getting data from the response
            count = 0
            # print(posts["posts"])
            print(posts)
            for post in posts["posts"]:
                # print("in foor loop")
                # print(post)
                count +=1
                # print(count)
                # check if the post is already saved in our db from a previous request
                # if it is, continue to next post. If it isn't, save it?

                # todo: grab the author from the post and create/save a new author objects
            
                # print(post["author"],1999)
                print("here")
                try:
                    # post_author =  CustomUser(timestamp= timezone.now(), id=post["author"]["id"].split("author/")[1], host=remote_server.host, displayname=post["author"]["displayName"], github_url=post["author"]["github"], username = post["author"]["id"].split("author/")[1], password= "12345" )
                    print("we get here")
                    post_author = Services.getAuthor(post["author"])
                    print("get here tho ?")

                # print(187)
                # there are a bunch of fields here that still need to be filled out
                
                    # print(post["content"],189)
                    # print((post["content"]),189)
                    post_object = Post(id=post["id"], author=post_author, title=post["title"], description=post["description"], body=post["content"], privacy_setting='6', published=post["published"], original_host=remote_server.host)
                    # print(192)
                    post_object.save()
                except Exception as e:
                    print(e,189)   
                remote_posts.append(post_object)

                # add each comment on the post to the post
                for comment in post["comments"]:
                    if comment != []:
                        try:
                            # comment_author =  CustomUser(timestamp= timezone.now(), id=comment["author"]["id"].split("author/")[1], host=remote_server.host, displayname=comment["author"]["displayName"], github_url=comment["author"]["github"], username = comment["author"]["id"].split("author/")[1], password= "12345" )
                            comment_author = Services.addAuthor(comment["author"])
                        except Exception as e:
                            print("author already exists")
                            pass
                        try:
                            # Probably make sure comments are not overwritte here
                            # AKA try to get the comment first
                            newComment = Comment()
                            newComment.body = comment["comment"]
                            newComment.post = post_object
                            # Does this need to be a custom user object?
                            # newComment.author = CustomUser.objects.get(pk=current_user_id)
                            newComment.author = comment_author
                            newComment.id = comment["id"]
                            newComment.datetime = comment["published"]
                            newComment.save()
                            print("NEW COMMENT:" , newComment)
                        except Exception as e:
                            print(e)
                            print("comment not being made properly")
            
    except:
        # No external servers or posts found
        print("No posts or no servers were found")

    # Lets just try to get all the comments in here instead
    # What could go wrong?
    # for post in remote_posts:
    #     get_remote_comments_by_post_id(post.id, current_user_id)

    return remote_posts



def get_remote_post_by_id(remote_post_id,current_user_id):
    

    # current strategy: get all posts from all connected servers
    # go through the posts and filter out ones that the current user
    # should not be able to see
    remote_posts = []
    try:
        queryset = Server.objects.all()
        for remote_server in queryset:
            request_url = remote_server.host + "/posts/%s" % remote_post_id
            header = get_custom_header_for_user(current_user_id)
            r = requests.get(request_url, auth=(remote_server.username, remote_server.password), headers=header)

            if r.status_code != 200:
                print("An error occured")
                continue
            
            posts = r.text.posts # hopefully this is the correct syntax for getting data from the response

            for post in posts:
                # check if the post is already saved in our db from a previous request
                # if it is, continue to next post. If it isn't, save it?

                # todo: grab the author from the post and create/save a new author object
                # post_author =  CustomUser(id=post["author"]["id"], host=remote_server.host,  displayname=post["author"]["displayname"], github=post["author"]["github_url"], username = post["author"]["displayname"], password= "12345", )
                # post_author.save()
                post_author = Services.addAuthor(post["author"])

                # there are a bunch of fields here that still need to be filled out
                post_object = Post(id=post.id, author=post_author, title=post.title, description=post.description, body=post.content, privacy_setting='6', published=post.published, original_host=remote_server.host)
                post_object.save()

                remote_posts.append(post_object)
            
    except:
        # No external servers or posts found
        print("No posts or servers were found")
    return remote_posts



def get_remote_comments_by_post_id(remote_post_id,current_user_id):
    # This takes a post id (remote or not honestly shouldn't matter)
    # Then it returns the list of comment objects for that post, possibly ordered
    # Ill try to copy the way you guys are doing it

    # Do we have to determine if we have permission to see the post?
    return # return here just in case
    try:
        # Create a list of the connected servers
        queryset = Server.objects.all()
        for remote_server in queryset:

            # We will continue to hammer their API using the next tag
            # until we have retreived all the comments
            allComments = []
            while True:
                # consider increasing the amount to grab per page with comments?size=
                request_url = remote_server.host + "/posts/%s/comments" % remote_post_id
                header = get_custom_header_for_user(current_user_id)
                r = requests.get(request_url, auth=(remote_server.username, remote_server.password), headers=header)

                if r.status_code != 200:
                    print("Requesting:", request_url, "Status:", r.status_code)
                    break
                
                # comments should be json for the comments
                # add them to the big list
                # I think you might be able to use the + operator but oh well
                comments = r.text.comments
                for comment in comments:
                    allComments.append(comment)
                
                # Find the URL to the next page
                # Obviously if the tag doesn't exist then break
                try:
                    # Cheap trick to see if this is a url and not null or ""
                    if len(r.text.next) > 10:
                        request_url = r.text.next
                    # If the url is none or null or "" or not long enogh to be a url
                    else:
                        break
                except:
                    break

            # For each comment in allComments, create a new comment object 
            # Then do we save it to the new post object that is saved in our database?
            # Probably
            for comment in allComments:
                print(comment)
                newComment = Comment()
                newComment.body = comment.body
                newComment.post = comment.post 
                # Does this need to be a custom user object?
                # newComment.author = CustomUser.objects.get(pk=current_user_id)
                newComment.author = current_user_id
                newComment.save()

    except:
        # No comments found
        print("No comments or servers found")

    return allComments