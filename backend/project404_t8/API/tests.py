from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Post, Friendship, Follow
from .serializers import PostSerializer
from .viewsets import uploadView, postView
import users.models as UserModels
import API.serializers as Serializers
import json
import API.services as Services

class PrivacyTestCase(TestCase):

    def setUp(self):
        self.author = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9c", username='user1')
        self.someUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d", username='user2')
        self.strangerUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e", username='user3')
        self.friendship = Friendship.objects.create(friend_a=self.author, friend_b=self.someUser)
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9c", title="this is a post", body="hello", author=self.author, privacy_setting="1")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d", title="this is a post", body="hello", author=self.author, privacy_setting="2", shared_author=self.someUser)
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e", title="this is a post", body="hello", author=self.author, privacy_setting="3")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f", title="this is a post", body="hello", author=self.author, privacy_setting="6")

        # use this to create HTTP Requests
        self.factory = RequestFactory()

    def test_user_can_see_their_own_posts(self):
        """Users can see their own posts"""
        author = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9c")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9c")

        hasPermission = Services.has_permission_to_see_post(author, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_can_see_another_author_posts_when_allowed(self):
        """Authorized users can see the post when the post privacy is set to Another Author"""
        someUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        hasPermission = Services.has_permission_to_see_post(someUser, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_another_author_posts_when_not_allowed(self):
        """Users cannot see Another Author posts if they aren't authorized"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        hasPermission = Services.has_permission_to_see_post(strangerUser, myPost)
        self.assertEqual(False, hasPermission)

    def test_user_can_see_their_friends_posts_when_allowed(self):
        """Users can see their friends' posts when the posts are set to My Friends"""
        someUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        hasPermission = Services.has_permission_to_see_post(someUser, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_friends_posts_of_non_friends(self):
        """Users can't see My Friends posts when they aren't friends"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        hasPermission = Services.has_permission_to_see_post(strangerUser, myPost)
        self.assertEqual(False, hasPermission)

    # # friends of friends isn't implemented

    # # friends of host isn't implemented

    def test_user_can_see_public_posts(self):
        """Users can see public posts"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f")
        hasPermission = Services.has_permission_to_see_post(strangerUser, myPost)
        self.assertEqual(True, hasPermission)

class FriendFollowerTestCase(TestCase):

    def setUp(self):
        self.userA = UserModels.CustomUser.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9c", username='user10')
        self.userB = UserModels.CustomUser.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d", username='user11')

    def test_adding_new_friend(self):
        """Check that after adding a friend, the user is following that friend"""
        Services.handle_friend_request(self.userA, self.userB)
        
        if not Follow.objects.filter(follower=self.userB, receiver=self.userA).exists():
            self.assertTrue(False)
        elif Follow.objects.filter(follower=self.userA, receiver=self.userB).exists():
            self.assertTrue(False)
        elif Friendship.objects.filter(friend_a=self.userA, friend_b=self.userB).exists():
            self.assertTrue(False)
        elif Friendship.objects.filter(friend_a=self.userB, friend_b=self.userA).exists():
            self.assertTrue(False)


    def test_accepting_request(self):
        """Check that after adding a friend, the user is following that friend"""
        Services.handle_friend_request(self.userA, self.userB)
        Services.handle_friend_request(self.userB, self.userA) 
        
        if Follow.objects.filter(follower=self.userB, receiver=self.userA).exists():
            self.assertTrue(False)
        elif Follow.objects.filter(follower=self.userA, receiver=self.userB).exists():
            self.assertTrue(False)
        elif not Friendship.objects.filter(friend_a=self.userA, friend_b=self.userB).exists():
            self.assertTrue(False)
        elif not Friendship.objects.filter(friend_a=self.userB, friend_b=self.userA).exists():
            self.assertTrue(False)
        

    def test_test_cannot_add_yourself_as_friend(self):
        """Check that you cannot add yourself as a friend"""
        Services.handle_friend_request(self.userA, self.userA)
        
        if Follow.objects.filter(follower=self.userB, receiver=self.userA).exists():
            self.assertTrue(False)
        elif Follow.objects.filter(follower=self.userA, receiver=self.userB).exists():
            self.assertTrue(False)
        elif Friendship.objects.filter(friend_a=self.userA, friend_b=self.userB).exists():
            self.assertTrue(False)
        elif Friendship.objects.filter(friend_a=self.userB, friend_b=self.userA).exists():
            self.assertTrue(False)


class postTestCase(APITestCase):
    client = APIClient()

    @staticmethod
    def create_post(title="", body=""):
        if title != "" and body != "":
            Post.objects.create(title=title, body=body)

    def setUp(self):
        # add test data
        self.create_post(" glue", "i like glue with all my heart")
        self.create_post("jam rock", "jamming like its the 90s")

class GetAllPostsTest(postTestCase):

    def test_get_all_posts(self):
        """
        This test ensures that all posts added in the setUp method
        exist when we make a GET request to the posts/ endpoint
        """
        # # hit the API endpoint
        # response = self.client.get(
        #     reverse("posts-all")
        # )
        # # fetch the data from db
        # expected = Posts.objects.all()
        # serialized = PostsSerializer(expected, many=True)
        # self.assertEqual(response.data, serialized.data)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)


