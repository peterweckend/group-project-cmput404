from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, UserManager

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
    username    = models.CharField(max_length=255, unique=True)
    password    = models.CharField(max_length=50)
    displayname = models.CharField(max_length=15)
    admin       = models.BooleanField(default=False) # superuser 
    timestamp   = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.admin

        