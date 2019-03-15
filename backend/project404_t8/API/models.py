from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save

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
        ('2', 'another author'),
        ('3', 'my friends'),
        ('4', 'friends of friends'),
        ('5', 'only friends on my host'),
        ('6', 'public'),
        ('7', 'unlisted')
    )

    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=250)
    body = models.TextField()
    # created_on = models.DateTimeField(auto_now=True)
    image_link = models.FileField(blank=True, null=True) # As an author, posts I create can link to images.
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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    datetime = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
            return '%s %s %s %s' % (self.id, self.author, self.post, self.datetime)


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

    def __str__(self):
        return '%s %s' % (self.follower, self.receiver)


class Server(models.Model):
    id = models.AutoField(primary_key=True)

    # todo: store a list of hosted images?

    def __str__(self):
        return '%s' % (self.id)



