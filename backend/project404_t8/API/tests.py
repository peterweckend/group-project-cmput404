from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Post, Friendship, Follow, Server
from .serializers import PostSerializer
from .viewsets import uploadView, postView
import users.models as UserModels
import API.serializers as Serializers
import json
import API.services as Services
import API.serverMethods as ServerMethods
import API.constants as constants

class PrivacyTestCase(TestCase):

    def setUp(self):
        self.author = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9c", username='user1')
        self.someUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d", username='user2')
        self.strangerUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e", username='user3')
        self.friendOfSomeUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9f", username='user4')
        self.friendOfFriendOfSomeUser = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9a", username='user5')
        self.friendship = Friendship.objects.create(friend_a=self.author, friend_b=self.someUser)
        self.friendship = Friendship.objects.create(friend_a=self.someUser, friend_b=self.author)
        self.friendship = Friendship.objects.create(friend_a=self.friendOfSomeUser, friend_b=self.someUser)
        self.friendship = Friendship.objects.create(friend_a=self.someUser, friend_b=self.friendOfSomeUser)
        self.friendship = Friendship.objects.create(friend_a=self.friendOfSomeUser, friend_b=self.friendOfFriendOfSomeUser)
        self.friendship = Friendship.objects.create(friend_a=self.friendOfFriendOfSomeUser, friend_b=self.friendOfSomeUser)
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9c", title="this is a post", body="hello", author=self.author, privacy_setting="1")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d", title="this is a post", body="hello", author=self.author, privacy_setting="2", shared_author=self.someUser)
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e", title="this is a post", body="hello", author=self.author, privacy_setting="3")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f", title="this is a post", body="hello", author=self.author, privacy_setting="6")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9a", title="this is a post", body="hello", author=self.author, privacy_setting="4")
        Post.objects.create(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9b", title="this is a post", body="hello", author=self.author, privacy_setting="7")

        # use this to create HTTP Requests
        self.factory = RequestFactory()

    def test_user_can_see_their_own_posts(self):
        """Users can see their own posts"""
        author = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9c")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9c")

        hasPermission = Services.has_permission_to_see_post(author.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_can_see_another_author_posts_when_allowed(self):
        """Authorized users can see the post when the post privacy is set to Another Author"""
        someUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        hasPermission = Services.has_permission_to_see_post(someUser.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_another_author_posts_when_not_allowed(self):
        """Users cannot see Another Author posts if they aren't authorized"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
        self.assertEqual(False, hasPermission)

    def test_user_can_see_their_friends_posts_when_allowed(self):
        """Users can see their friends' posts when the posts are set to My Friends"""
        someUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9d")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        hasPermission = Services.has_permission_to_see_post(someUser.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_cannot_see_friends_posts_of_non_friends(self):
        """Users can't see My Friends posts when they aren't friends"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
        self.assertEqual(False, hasPermission)
    
    def test_users_should_be_able_to_see_unlisted(self):
        # has_permission_to_see_post wouldn't be called if they didn't know the url
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9b")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_can_see_public_posts(self):
        """Users can see public posts"""
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_user_can_see_fof_posts(self):
        friendOfSomeUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9f")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9a")
        hasPermission = Services.has_permission_to_see_post(friendOfSomeUser.id, myPost)
        self.assertEqual(True, hasPermission)

    def test_nonfriend_cant_see_fof_posts(self):
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9a")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
        self.assertEqual(False, hasPermission)

    def test_fofof_cant_see_fof_posts(self):
        friendOfFriendOfSomeUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9a")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9a")
        hasPermission = Services.has_permission_to_see_post(friendOfFriendOfSomeUser.id, myPost)
        self.assertEqual(False, hasPermission)

    def test_permissions_work_with_non_uuid(self):
        # essentially test that we can pass in a string (instead of a UUID) without the function crashing
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f")
        hasPermission = Services.has_permission_to_see_post("8c4f71d9-fcc5-48b0-8092-9b775969bc9e", myPost)
        # if we get here, there hasn't been an error
        self.assertEqual(True, hasPermission)

    def test_permissions_work_with_uuid(self):
        # essentially test that we can pass in a UUID without the function crashing
        # This is currently the same as an above test and uuid functionality is implicitly tested by other tests
        # but I want to make sure this is explicitly tested in case the above tests change
        strangerUser = UserModels.CustomUser.objects.get(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9e")
        myPost = Post.objects.get(id="9c4f71d9-fcc5-48b0-8092-9b775969bc9f")
        hasPermission = Services.has_permission_to_see_post(strangerUser.id, myPost)
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


class hostTestCase(TestCase):

    def setUp(self):
        self.author = UserModels.CustomUser.objects.create(id="8c4f71d9-fcc5-48b0-8092-9b775969bc9c", username='user1')
        self.localServer = Server.objects.create(id="1c4f71d9-fcc5-48b0-8092-9b775969bc9d", host='127.0.0.1', username=constants.LOCAL_USERNAME, password='password')
        self.otherServer = Server.objects.create(id="1c4f71d9-fcc5-48b0-8092-9b775969bc9e", host='128.0.0.1', username='nonlocal', password='password2')

    def test_xuser_header_built_correctly(self):
        expected_header = {}
        expected_header["X-User"] = "127.0.0.1/author/8c4f71d9-fcc5-48b0-8092-9b775969bc9c"
        self.assertEqual(ServerMethods.get_custom_header_for_user(self.author.id), expected_header)

    def test_returns_local_server(self):
        server = Server.objects.filter(id = self.localServer.id)[0]
        otherServer = Server.objects.filter(id = self.otherServer.id)[0]
        self.assertEqual(ServerMethods.get_our_server(), server)
        self.assertNotEqual(ServerMethods.get_our_server(), otherServer)

    def test_returns_correct_server_information(self):
        server = Server.objects.filter(id = self.localServer.id)[0]
        otherServer = Server.objects.filter(id = self.otherServer.id)[0]
        self.assertEqual(ServerMethods.get_server_info(server.host), server)
        self.assertNotEqual(ServerMethods.get_server_info(server.host), otherServer)


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

    # ('1', 'me'),
    # ('2', 'another author'),
    # ('3', 'my friends'),
    # ('4', 'friends of friends'),
    # ('5', 'only friends on my host'),
    # ('6', 'public'),
    # ('7', 'unlisted')
    # ["PRIVATE", "FRIENDS", "FOAF", "SERVERONLY", "PUBLIC"]
    def test_correct_privacy_string_returned(self):
        self.assertEqual(Services.get_privacy_string_for_post("1"), "PRIVATE")
        self.assertEqual(Services.get_privacy_string_for_post("2"), "PRIVATE")
        self.assertEqual(Services.get_privacy_string_for_post("3"), "FRIENDS")
        self.assertEqual(Services.get_privacy_string_for_post("4"), "FOAF")
        self.assertEqual(Services.get_privacy_string_for_post("5"), "SERVERONLY")
        self.assertEqual(Services.get_privacy_string_for_post("6"), "PUBLIC")

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


