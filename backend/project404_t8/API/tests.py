from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Post
from .serializers import PostSerializer
from .viewsets import uploadView, postView
import users.models as UserModels
import API.serializers as Serializers
import json
import API.services as Services

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

class PrivacyTestCase(TestCase):

    def setUp(self):
        self.userTestModel = UserTestModel()
        self.author = UserModels.CustomUser.objects.create(id=100, username='user1')
        Post.objects.create(id=1000, title="this is a post", body="hello", author=self.author, privacy_setting="1")

        # use this to create HTTP Requests
        self.factory = RequestFactory()

    def test_post_view(self):
        # # """Users can see their own posts"""
        myPost = Post.objects.get(id=1000)

        hasPermission = Services.has_permission_to_see_post(100, myPost)
        self.assertEqual(True, hasPermission)

