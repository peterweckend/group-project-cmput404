from .models import Post, Comment, Friendship, Follow, Server

# Exists between the data layers and the UI.
# Holds the logic of the views.
# This allows multiple views to access the same functions
# and logic easily and allows us to change the logic all in one place.

def has_permission_to_see_post(requesting_user_id, post):
    hasPermission = False

    # ('1', 'me'),
    # This one will always apply, so it does not need an if conditional
    if requesting_user_id == post.author.id:
        hasPermission = True

    # ('2', 'another author'),
    if post.privacy_setting == '2':
        if requesting_user_id == post.author or requesting_user_id == post.shared_author.id:
            hasPermission = True

    # ('3', 'my friends'),
    # So first get the IDs of all the author's friends
    if post.privacy_setting == '3':
        # Get a list of all the rows in friends where friend_a/b == requesting_user_id
        friends1 = Friendship.objects.filter(friend_a=post.author.id)
        friends2 = Friendship.objects.filter(friend_b=post.author.id)
        friends = set()
        # alright this feels really messy but it should work I think
        # If the models change things could get cringed but I actually think its fine
        # Iterate through each queryset, and append the ids of each element to the list
        for row in friends1:
            friends.add(row.friend_b.id)
        for row in friends2:
            friends.add(row.friend_a.id)

        # Friends are the authors friends
        # If the requester is in the friends list they can view
        if requesting_user_id in friends:
            # print(requesting_user_id, friends)
            hasPermission = True

    # ('4', 'friends of friends'),
    # This is brutal enough to do in SQLite, how tf do we do it in Django???
    # Can just bruteforce it I guess lol, for each user in authorsfriends
    # query all their friends then add to another set

    # ('5', 'only friends on my host'),
    # Not sure how to implement this one, how do we know where the user's hosted on?
    # This is a problem for the next deadline lel

    # ('6', 'public')
    # ('7', 'unlisted')
    # The special thing about unlisted is the URL must be complicated or hard to guess
    if post.privacy_setting in ["6","7"]:
        hasPermission = True

    return True