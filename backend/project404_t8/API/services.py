from .models import Post, Comment, Friendship, Follow, Server
from users.models import CustomUser
import uuid
from urllib.parse import urlparse
from django.utils import timezone

# Exists between the data layers and the UI.
# Holds the logic of the views.
# This allows multiple views to access the same functions
# and logic easily and allows us to change the logic all in one place.

def has_permission_to_see_post(requesting_user_id, post):
    hasPermission = False

    # convert to UUID object
    if not isinstance(requesting_user_id, uuid.UUID):
        try:
            requesting_user_id = uuid.UUID(requesting_user_id)
        except:
            print("An error occurred.")
            return False

    # do we need to replace the '-'s in requesting_user_id? probably not but maybe?

    # ('1', 'me'),
    # This one will always apply, so it does not need an if conditional
    if requesting_user_id == post.author.id:
        hasPermission = True

    # ('2', 'another author'),
    if post.privacy_setting == '2':
        if requesting_user_id == post.author.id or requesting_user_id == post.shared_author.id:
            hasPermission = True

    # ('3', 'my friends'),
    # So first get the IDs of all the author's friends
    if post.privacy_setting == '3' or post.privacy_setting == '4':
        # Get a list of all the rows in friends where friend_a/b == requesting_user_id
        friends1 = Friendship.objects.filter(friend_a=post.author.id)
        friends2 = Friendship.objects.filter(friend_b=post.author.id)
        friends = set()
        # alright this feels really messy but it should work I think
        # If the models change things could get cringed but I actually think its fine
        # Iterate through each queryset, and append the ids of each element to the list
        friendObj = []
        for row in friends1:
            friends.add(row.friend_b.id)
            friendObj.append(row)
        for row in friends2:
            friends.add(row.friend_a.id)
            friendObj.append(row)

        # Friends are the authors friends
        # If the requester is in the friends list they can view
        if requesting_user_id in friends:
            hasPermission = True

        # ('4', 'friends of friends'),
        # This is brutal enough to do in SQLite, how tf do we do it in Django???
        # Can just bruteforce it I guess lol, for each user in authorsfriends
        # query all their friends then add to another set
        if post.privacy_setting == '4':
            for friend in friendObj:
                friends1 = Friendship.objects.filter(friend_a=friend.friend_a.id)
                friends2 = Friendship.objects.filter(friend_b=friend.friend_b.id)

                for row in friends1:
                    friends.add(row.friend_b.id)
                for row in friends2:
                    friends.add(row.friend_a.id)
            if requesting_user_id in friends:
                hasPermission = True

    # ('5', 'only friends on my host'),
    # Not sure how to implement this one, how do we know where the user's hosted on?
    # This is a problem for the next deadline lel
    # TODO
    # basically same as friends above, but make sure they are from the connectify host

    # ('6', 'public')
    # ('7', 'unlisted')
    # The special thing about unlisted is the URL must be complicated or hard to guess
    # Something can be unlisted but not private, so this is separate logic here

    if post.privacy_setting in ["6","7"]:
        hasPermission = True

    return hasPermission


def handle_friend_request(receiver_user, follower_user):
    # Do nothing if a friendship between the two users exists
    
    check1 = Friendship.objects.filter(friend_a=receiver_user, friend_b=follower_user)
    check2 = Friendship.objects.filter(friend_b=receiver_user, friend_a=follower_user)

    if check1.exists() or check2.exists():
        # Friendship already exists, so do nothing
        return
  
    # Do nothing if the follow relationship already exists
    check1 = Follow.objects.filter(receiver=receiver_user, follower=follower_user)
    if check1.exists():
        # Follow / friend request already exists, do nothing
        return

    # If the inverse relationship exists, remove it,
    # Then add the relationship to friends instead
    # So first, query for the relationship
    if Follow.objects.filter(follower=receiver_user, receiver=follower_user).exists():
        # Delete this entry, then create a friend relationship instead
        follow = Follow.objects.get(follower=receiver_user, receiver=follower_user)
        follow.delete()
        friend = Friendship(friend_a=follower_user, friend_b=receiver_user)
        friend.save()

        # Addition by TOLU
        # we have to add this because we need the relationship going both ways
        # for the database SQL queries of friend of friends
        friend = Friendship(friend_a=receiver_user, friend_b=follower_user)
        friend.save()
        

    # maybe make sure the user cant send a new friend request after already
    # being friends
    else:
        # Create the entry in follow, essentially sending the friend request
        follow = Follow(follower=follower_user, receiver=receiver_user)
        follow.save()

    updateNotificationsById(receiver_user.id)
    updateNotificationsById(follower_user.id)

# In theory this should update notifications by object, not ID
# But its fine for now, dont fix what isnt broken 
def updateNotificationsById(id):
    user = CustomUser.objects.get(id=id)
    total = Follow.objects.filter(receiver=user.id, ignored=0)
    total = len(total)
    user.friend_requests = total
    user.save()

def isNotBlank (myString):
        return bool(myString and myString.strip())

# returns the size of results the query wants to display, &size=
def get_page_size(request, paginator):
    if (request.GET.get('size')):
        return int(request.GET.get('size'))
    else:
        return paginator.page_size


# pass in a string containing the post's privacy value (ex: "3")
# this function will return the corresponding API privacy text value (ex: "FRIENDS")
#         ('1', 'me'),
#         ('2', 'another author'),
#         ('3', 'my friends'),
#         ('4', 'friends of friends'),
#         ('5', 'only friends on my host'),
#         ('6', 'public'),
#         ('7', 'unlisted')
def get_privacy_string_for_post(post_privacy_value):
    visibility = ["PRIVATE", "FRIENDS", "FOAF", "SERVERONLY", "PUBLIC"]
    if post_privacy_value == "1":
        return visibility[0]
    elif post_privacy_value == "2":
        return visibility[0]
    elif post_privacy_value == "3":
        return visibility[1]
    elif post_privacy_value == "4":
        return visibility[2]
    elif post_privacy_value == "5":
        return visibility[3]
    elif post_privacy_value == "6":
        return visibility[4]
    elif post_privacy_value == "7": # TODO: see what happens to option 7
        return "-1"
    else:
        return "-1"

# Takes a JSON representation of an author as served in the API spec
# Adds the author if it does not exist and returns it
# Otherwise returns the existing author
# Otherwise does nothing (as the author already exists !)
def addAuthor(authorJSON):

    author = authorJSON

    try:
        author = CustomUser.objects.get(pk=author["id"].split("/")[-1])
        return author

    except:
        host = urlparse(author["url"]).hostname 

        author = CustomUser(
            timestamp = timezone.now(),
            id = author["id"].split("/")[-1],
            username = author["id"].split("/")[-1],
            password = "fixme",
            displayname = author["displayName"],
            host = host,
            github_url=author["github"],
        )
        author.save()
        return author

# Takes a JSON representation of a post as served in the API spec
# Adds the post if it does not exist and returns it
# Otherwise returns the existing post
# What are we going to do with image data here? Surely we cannot save it as a giant full string!

# Issue rn, if the content type is image, fucked shit happens
def addPost(postJSON):

    post = postJSON
# post_object = Post(id=post["id"], author=post_author, title=post["title"], description=post["description"], body=post["content"], privacy_setting='6', published=post["published"], original_host=remote_server.host)

    try:
        post_object = Post.objects.get(pk=post["id"])
        return post_object
    except:
        parsed = urlparse(post["origin"])
        origin =  parsed.scheme + "://" + parsed.netloc
        post_author = CustomUser.objects.get(pk=post["author"]["id"].split("/")[-1])

        # Prevent fucky shit shit encoded images
        # TODO decode/save the image somehow
        if post["contentType"] not in ["text/plain", "text/markdown"]:
            post["content"] = "THIS SHOULD BE AN IMAGE SOMEHOW"        

        post_object = Post(
            id = post["id"],
            author = post_author, 
            title = post["title"], 
            description = post["description"], 
            body = post["content"], 
            privacy_setting = '6', # Hardcoded for now lel, not looking good
            published = post["published"], 
            original_host = origin
        )
        post_object.save()
        return post