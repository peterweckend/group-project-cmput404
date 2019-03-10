from django.db import models

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    body = models.TextField()

    def __str__(self):
            return '%s %s' % (self.title, self.body)


class User(models.Model):
    id = models.AutoField


class Server(models.Model):

