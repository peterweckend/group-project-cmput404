from rest_framework import routers
from API.viewsets import PostViewSet

router = routers.DefaultRouter()

router.register(r'API', PostViewSet)
