from rest_framework import serializers
from .models import Posts, User, Comment, Friendship, Follow, Server



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
    # id = serializers.ReadOnlyField()
    # username = serializers.CharField()
    # display_name = serializers.CharField()
    # # this might have to be changed
    # password = serializers.CharField()


class PostsSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    # title = serializers.CharField()
    # body = serializers.CharField()
    # image_link = serializers.CharField(required=False, allow_blank=True)
    # privacy_setting = serializers.CharField()
    # shared_author = serializers...
    # is_markdown = serializers.BooleanField()
    class Meta:
        model = Posts


class CommentSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    # author = serializers.
    # post = 
    class Meta:
        model = Comment


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow


class ServerSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    class Meta:
        model = Server