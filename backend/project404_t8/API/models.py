from django.db import models
from datetime import datetime



class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.TextField(default='Username')
    display_name = models.TextField(default='User')
    password = models.TextField(default='password')

    def __str__(self):
        return '%s' % (self.id)


class Post(models.Model):

    PRIVACYCHOICE = (
        ('1', 'me'),
        ('2', 'another author'),
        ('3', 'my friends'),
        ('4', 'friends of friends'),
        ('5', 'only friends on my host'),
        ('6', 'public'),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    body = models.TextField()
    image_link = models.TextField(blank=True, null=True) # As an author, posts I create can link to images.

    privacy_setting = models.CharField(max_length=1, choices=PRIVACYCHOICE, default='1')

    # This is null if privacy_setting != 2. Specifies the ID of the shared author.
    shared_author = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True) 

    # If true, post can be in markdown
    is_markdown = models.BooleanField(default=False)


    def __str__(self):
        return '%s %s %s %s %s %s %s' % (self.id, self.title, self.body, self.image_link, 
            self.privacy_setting, self.shared_author, self.is_markdown)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
            return '%s %s %s %s' % (self.id, self.author, self.post, self.datetime)


# This is when you befriend someone and they befriend you
# (Friend another author and they accept the friend request)
# When the friend request is accepted, the corresponding Follow model is deleted
class Friendship(models.Model):
    friend_a = models.ForeignKey(User, related_name="friend_a_set", on_delete=models.CASCADE)
    friend_b = models.ForeignKey(User, related_name="friend_b_set", on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s' % (self.friend_a, self.friend_b)


# This is when you befriend someone
# (Friend another author without an accepted friend request)
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="follower_set", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver_set", on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s' % (self.follower, self.receiver)


class Server(models.Model):
    id = models.AutoField(primary_key=True)

    # todo: store a list of hosted images?

    def __str__(self):
        return '%s' % (self.id)


