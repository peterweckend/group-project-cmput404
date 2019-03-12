from rest_framework import serializers
from .models import Post, User, Comment, Friendship, Follow, Server
# REST API Serializer JSON https://www.youtube.com/watch?v=V4NjlXiu5WI



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  
    # id = serializers.ReadOnlyField()
    # username = serializers.CharField()
    # display_name = serializers.CharField()
    # # this might have to be changed
    # password = serializers.CharField()


class PostSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    # title = serializers.CharField()
    # body = serializers.CharField()
    # image_link = serializers.CharField(required=False, allow_blank=True)
    # privacy_setting = serializers.CharField()
    # shared_author = serializers...
    # is_markdown = serializers.BooleanField()
    class Meta:
        model = Post
        fields = '__all__' 


class CommentSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    # author = serializers.
    # post = 
    class Meta:
        model = Comment
        fields = '__all__' 


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__' 


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__' 


class ServerSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    class Meta:
        model = Server
        fields = '__all__' 