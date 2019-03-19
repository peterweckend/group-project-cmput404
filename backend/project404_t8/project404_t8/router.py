from rest_framework import routers
from API.viewsets import UserViewSet, PostViewSet, CommentViewSet, FriendshipViewSet, FollowViewSet, ServerViewSet, uploadView, postView

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, base_name='user')
router.register(r'post', PostViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'friendship', FriendshipViewSet)
router.register(r'follow', FollowViewSet)
router.register(r'server', ServerViewSet)