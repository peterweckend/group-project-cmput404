from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import DateTimeField, BooleanField


# @receiver(post_save, sender=User)
# def create_author_profile(sender, instance, created, **kwargs):
#     if created:
#         Author.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_author_profile(sender, instance, **kwargs):
#     instance.author.save()

class Post(models.Model):

    PRIVACYCHOICE = (
        ('1', 'me'),
        ('2', 'specific users'),            # PRIVATE OPTION
        ('3', 'my friends'),
        ('4', 'friends of friends'),
        ('5', 'only friends on my host'),   # SERVER ONLY OPTION
        ('6', 'public'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField(default="") # a description of what the post is about
    body = models.TextField() # the actual content of the post
    # created_on = models.DateTimeField(auto_now=True)
    image_link = models.FileField(blank=True, null=True) # As an author, posts I create can link to images.
    privacy_setting = models.CharField(max_length=1, choices=PRIVACYCHOICE, default='1')

    # This is null if privacy_setting != 2. Specifies the ID of the shared author.
    shared_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='shared_author') 

    # If true, post can be in markdown
    is_markdown = models.BooleanField(default=False)
    is_unlisted = models.BooleanField(default=False)
    published = DateTimeField(auto_now_add=True)

    # if this post came from another server, store the original host here
    original_host = models.TextField()


    def __str__(self):
        return '%s %s %s %s %s %s %s %s' % (self.id, self.title, self.body, self.image_link, 
            self.privacy_setting, self.shared_author, self.is_markdown, self.is_unlisted)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True,related_name="comments")
    datetime = models.DateTimeField(default=datetime.now, blank=True)
    body = models.TextField(default="")
    is_markdown = models.BooleanField(default=False)

    def __str__(self):
            return '%s %s %s %s' % (self.id, self.author, self.post, self.datetime)

class PostCategory(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True,related_name="post_cat_id")
    category = models.TextField(max_length=250)

class PostAuthorizedAuthor(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True,related_name="post_auth_author_id")
    authorized_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='post_viewable_author') 

# This is when you befriend someone and they befriend you
# (Friend another author and they accept the friend request)
# When the friend request is accepted, the corresponding Follow model is deleted
class Friendship(models.Model):
    friend_a = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_a_set", on_delete=models.CASCADE,blank=True, null=True)
    friend_b = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_b_set", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.friend_a, self.friend_b)


# This is when you befriend someone
# (Friend another author without an accepted friend request)
class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="follower_set", on_delete=models.CASCADE, blank=True, null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="receiver_set", on_delete=models.CASCADE, blank=True, null=True)
    ignored = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.follower, self.receiver)


class Server(models.Model):
    id = models.UUIDField(primary_key=True,editable=False, default=uuid.uuid4)
    host = models.URLField(unique=True, default="")
    username = models.TextField(max_length=255, unique=True, default="")
    password = models.CharField(max_length=255, default="") # this should be hashed but for now its plaintext

    def __str__(self):
        return '%s %s' % (self.id  ,self.host)


