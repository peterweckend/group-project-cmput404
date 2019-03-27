from .models import Server
from users.models import CustomUser
import requests
import API.services as Services

# returns a header object of the format:
# X-User: http://service/author/:uuid
# this should be included in the headers of 
# any requests that involve checking permissions
LOCAL_USERNAME = 'heroku'
def get_custom_header_for_user(user_id):
    try:
        queryset = Server.objects.filter(username=LOCAL_USERNAME)
        server = ServerSerializer(queryset, many=True).data[0]
        header = {'X-User': server.host + "/author/" + str(user_id)}
        return header
    except:
        print("An error occurred generating the custom header.")
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


def get_remote_author(remote_server, remote_author_id):
    request_url = remote_server.host + "/author/" + str(remote_author_id)
    r = requests.get(request_url, auth=(remote_server.username, remote_server.password))
    if r.status_code == 200:
        response = r.text
        remote_author = CustomUser(id=remote_author_id, host=remote_server.host, \
            displayname=response.displayName, github=response.github, username = remote_author_id, \
            password= "12345", bio=response.bio)
        remote_author.save()
        return remote_author
    else:
        return None

# returns a second parameter stating if the author is local
def get_user(remote_author_id):
    # search for any local authors with the username
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
def befriend_remote_author(remote_author_id, local_author_id):

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
        Services.handle_friend_request(remote_author.username, local_author.username)
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
    remote_posts = []
    try:
        queryset = Server.objects.all()
        for remote_server in queryset:
            request_url = remote_server.host + "/author/posts"
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
                post_author =  CustomUser(id=post["author"]["id"], host=remote_server.host, \
                            displayname=post["author"]["displayname"], github=post["author"]["github_url"], username = post["author"]["displayname"], \
                            password= "12345", )
                post_author.save()

                # there are a bunch of fields here that still need to be filled out
                post_object = Post(id=post.id, author=post_author, title=post.title, description=post.description, body=post.content, privacy_setting='6', published=post.published, original_host=remote_server.host)
                post_object.save()

                remote_posts.append(post_object)
            
    except:
        # No external servers or posts found
        print("No posts or servers were found")
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
                post_author =  CustomUser(id=post["author"]["id"], host=remote_server.host,  displayname=post["author"]["displayname"], github=post["author"]["github_url"], username = post["author"]["displayname"], password= "12345", )
                post_author.save()

                # there are a bunch of fields here that still need to be filled out
                post_object = Post(id=post.id, author=post_author, title=post.title, description=post.description, body=post.content, privacy_setting='6', published=post.published, original_host=remote_server.host)
                post_object.save()

                remote_posts.append(post_object)
            
    except:
        # No external servers or posts found
        print("No posts or servers were found")
    return remote_posts



def get_remote_comments_by_post_id(remote_post_id):
    return None