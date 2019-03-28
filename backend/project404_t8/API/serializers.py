from rest_framework import serializers
from .models import Post, Comment, Friendship, Follow, Server, PostCategory, PostAuthorizedAuthor
# REST API Serializer JSON https://www.youtube.com/watch?v=V4NjlXiu5WI
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__' #['id', 'username', 'password', 'last_login']
        # "id", "last_login", "is_superuser", "first_name", "last_name", 
        # "email", "is_staff", "is_active", "date_joined", "username", 
        # "password", "admin", "timestamp", "groups", "user_permissions"
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__' 


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__' 

class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = '__all__' 

class PostAuthorizedAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAuthorizedAuthor
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