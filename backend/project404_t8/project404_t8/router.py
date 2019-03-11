from rest_framework import routers
from API.viewsets import PostViewSet,uploadView

router = routers.DefaultRouter()

router.register(r'post', PostViewSet)
# router.register(r'upload',uploadView)