from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Posts
from .serializers import PostsSerializer
# Create your tests here.

class postTestCase(APITestCase):
    client = APIClient()

    @staticmethod
    def create_post(title="", body=""):
        if title != "" and body != "":
            Posts.objects.create(title=title, body=body)

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
        # hit the API endpoint
        response = self.client.get(
            reverse("posts-all")
        )
        # fetch the data from db
        expected = Posts.objects.all()
        serialized = PostsSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
