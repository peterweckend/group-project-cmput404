from django.db import models

# Create your models here.
# Create your models here.
class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_heading = models.CharField(max_length=250)
    post_body = models.TextField()
    
def __str__(self):
        return '%s %s' % (self.post_heading, self.post_body)