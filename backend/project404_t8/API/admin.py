from django.contrib import admin
from .models import User, Post, Comment, Friendship, Follow, Server
# Register your models here.

admin.site.register(User)

# Added for testing. Can be removed later -tolu
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Friendship)
admin.site.register(Follow)
admin.site.register(Server)
