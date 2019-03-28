from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, UserManager
import uuid
# from API.models import Server

# https://youtu.be/HshbjK1vDtY
class CustomUserManager(UserManager):
    def create_user(self, username, email, password=None, is_admin=False):
        if not username:
            raise ValueError("Users must have a username")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
            username = username
        )
        user_obj.set_password(password) # change user password
        user_obj.save(using=self._db)
        return user_obj


class CustomUser(AbstractUser):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username    = models.CharField(max_length=255, unique=True)
    password    = models.CharField(max_length=255)
    displayname = models.CharField(max_length=255, blank=True)
    first_name  = models.CharField(max_length=256)
    last_name   = models.CharField(max_length=256)
    password    = models.CharField(max_length=500)
    admin       = models.BooleanField(default=False) # superuser 
    timestamp   = models.DateTimeField(auto_now_add=True)
    friend_requests = models.CharField(max_length=100,default=0)
    github_id   = models.CharField(max_length=255)
    github_url  = models.CharField(max_length=512)
    host        = models.TextField()
    bio         = models.TextField()
    is_approved_by_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.admin

    # def get_url_to_author(self):
    #     author_host = self.host
    #     if not author_host:
    #         queryset = Server.objects.all()
    #         for server in queryset:
    #             if server.username == "local":
    #                 author_host = server.host
    #                 break
            
    #     return author_host + "author/" + str(self.id)


        