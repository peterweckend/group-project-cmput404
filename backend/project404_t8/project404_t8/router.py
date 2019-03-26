from rest_framework import routers
import API.viewsets as Viewsets

# these are the API methods
api_router = routers.SimpleRouter()
api_router.register(r'posts', Viewsets.PostsViewSet)
api_router.register(r'author', Viewsets.AuthorViewSet)

