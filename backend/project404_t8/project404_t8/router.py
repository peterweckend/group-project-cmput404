from rest_framework import routers
import API.viewsets as Viewsets

router = routers.DefaultRouter()

router.register(r'user', Viewsets.UserViewSet, base_name='user')
router.register(r'post', Viewsets.PostViewSet)
router.register(r'comment', Viewsets.CommentViewSet)
router.register(r'friendship', Viewsets.FriendshipViewSet)
router.register(r'follow', Viewsets.FollowViewSet)
router.register(r'server', Viewsets.ServerViewSet)

api_router = routers.SimpleRouter()
api_router.register(r'posts', Viewsets.PostsViewSet)
api_router.register(r'author', Viewsets.AuthorViewSet)

