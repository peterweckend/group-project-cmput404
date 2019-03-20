from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Post, Friendship
from .serializers import PostSerializer
from .viewsets import uploadView, postView
import users.models as UserModels
import API.serializers as Serializers
import json
import API.services as Services

class PrivacyTestCase(TestCase):

    def setUp(self):
        self.userTestModel = UserTestModel()
        self.author = UserModels.CustomUser.objects.create(id=100, username='user1')
        self.someUser = UserModels.CustomUser.objects.create(id=101, username='user2')
        self.strangerUser = UserModels.CustomUser.objects.create(id=102, username='user3')
        self.friendship = Friendship.objects.create(friend_a=self.author, friend_b=self.someUser)
        Post.objects.create(id=1001, title="this is a post", body="hello", author=self.author, privacy_setting="1")
        Post.objects.create(id=1002, title="this is a post", body="hello", author=self.author, privacy_setting="2", shared_author=self.someUser)
        Post.objects.create(id=1003, title="this is a post", body="hello", author=self.author, privacy_setting="3")
        Post.objects.create(id=1006, title="this is a post", body="hello", author=self.author, privacy_setting="6")

        # use this to create HTTP Requests
        self.factory = RequestFactory()

    def test_user_can_see_their_own_posts(self):
        """Users can see their own posts"""
        myPost = Post.objects.get(id=1001)

        hasPermission = Services.has_permission_to_see_post(100, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_can_see_another_author_posts_when_allowed(self):
        """Authorized users can see the post when the post privacy is set to Another Author"""
        myPost = Post.objects.get(id=1002)

        hasPermission = Services.has_permission_to_see_post(101, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_another_author_posts_when_not_allowed(self):
        """Users cannot see Another Author posts if they aren't authorized"""
        myPost = Post.objects.get(id=1002)
        hasPermission = Services.has_permission_to_see_post(102, myPost)
        self.assertEqual(False, hasPermission)

    def test_user_can_see_their_friends_posts_when_allowed(self):
        """Users can see their friends' posts when the posts are set to My Friends"""
        myPost = Post.objects.get(id=1003)
        hasPermission = Services.has_permission_to_see_post(101, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_friends_posts_of_non_friends(self):
        """Users can't see My Friends posts when they aren't friends"""
        myPost = Post.objects.get(id=1003)
        hasPermission = Services.has_permission_to_see_post(102, myPost)
        self.assertEqual(False, hasPermission)

    # friends of friends isn't implemented

    # friends of host isn't implemented

    def test_user_can_see_public_posts(self):
        """Users can see public posts"""
        myPost = Post.objects.get(id=1006)
        hasPermission = Services.has_permission_to_see_post(102, myPost)
        self.assertEqual(True, hasPermission)

class postTestCase(APITestCase):
    client = APIClient()

    @staticmethod
    def create_post(title="", body=""):
        if title != "" and body != "":
            Post.objects.create(title=title, body=body)

    def setUp(self):
        # add test data
        self.create_post(" glue", "i like glue with all my heart")
        self.create_post("simple post", "ben is a loser")
        self.create_post("love is wicked", "that hoe is a bitch")
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

class FriendTestCase(TestCase):
    def setUp(self):
        # Animal.objects.create(name="lion", sound="roar")
        # Animal.objects.create(name="cat", sound="meow")
        return None

    def test_something(self):
        # """Animals that can speak are correctly identified"""
        # lion = Animal.objects.get(name="lion")
        # cat = Animal.objects.get(name="cat")
        # self.assertEqual(lion.speak(), 'The lion says "roar"')
        # self.assertEqual(cat.speak(), 'The cat says "meow"')
        return None

# todo: refactor this
class UserTestModel():
        user = None

